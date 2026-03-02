import logging
import uuid
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from urllib.request import urlopen

import yaml
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.db.models import Q

from rea_vendors.models import Shop
from rea_catalog.models import Product, Category
from rea_eav.models import Parameter, ProductParameter

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    """Результат импорта"""
    success: bool
    message: str
    shop_id: Optional[str] = None
    products_created: int = 0
    products_updated: int = 0
    categories_created: int = 0
    categories_found: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ImportProductsService:
    """
    Сервис для импорта товаров поставщика из YAML файла
    """
    
    # Маппинг полей из файла в модель Product
    PRODUCT_FIELD_MAPPING = {
        'name': 'label',
        'model': 'model',
        'price': 'price',
        'price_rrc': 'price_rrc',
        'quantity': 'stock',
    }
    
    def __init__(self, user):
        self.user = user
        self.shop = None
        self.statistics = {
            'products_created': 0,
            'products_updated': 0,
            'categories_created': 0,
            'categories_found': 0,
            'parameters_created': 0,
            'errors': []
        }
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """
        Проверка корректности URL
        """
        validate_url = URLValidator()
        try:
            validate_url(url)
            return True, ""
        except ValidationError as e:
            return False, str(e)
    
    def fetch_and_parse_yaml(self, url: str) -> Tuple[bool, Any, str]:
        """
        Загрузка и парсинг YAML файла
        """
        try:
            response = urlopen(url)
            data = yaml.safe_load(response.read())
            return True, data, ""
        except Exception as e:
            error_msg = f"Ошибка при загрузке или парсинге YAML: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def validate_data_structure(self, data: Dict) -> Tuple[bool, str]:
        """
        Проверка структуры загруженных данных
        """
        required_keys = ['shop', 'categories', 'goods']
        
        for key in required_keys:
            if key not in data:
                return False, f"Отсутствует обязательный ключ '{key}' в файле"
        
        if not isinstance(data['categories'], list):
            return False, "Поле 'categories' должно быть списком"
        
        if not isinstance(data['goods'], list):
            return False, "Поле 'goods' должно быть списком"
        
        return True, ""
    
    def validate_uuid(self, uuid_str: str) -> bool:
        """
        Проверка корректности UUID
        """
        try:
            uuid.UUID(uuid_str)
            return True
        except (ValueError, TypeError):
            return False
    
    @transaction.atomic
    def process_categories(self, categories_data: List[Dict], shop: Shop) -> Dict[str, Category]:
        """
        Обработка категорий из импортируемых данных
        Возвращает маппинг UUID категорий на объекты Category
        
        Логика работы:
        1. Если категория с указанным UUID существует в БД → используем её
        2. Если категории с таким UUID нет → создаем новую с указанным UUID и именем
        """
        category_mapping = {}
        
        for cat_data in categories_data:
            category_uuid = cat_data.get('id')
            name = cat_data.get('name')
            
            if not category_uuid or not name:
                self.statistics['errors'].append(f"Пропущена категория с некорректными данными: {cat_data}")
                continue
            
            # Проверяем валидность UUID
            if not self.validate_uuid(category_uuid):
                self.statistics['errors'].append(
                    f"Пропущена категория '{name}': некорректный UUID '{category_uuid}'"
                )
                continue
            
            try:
                # Пытаемся найти категорию по UUID
                category = Category.objects.get(pk=category_uuid)
                self.statistics['categories_found'] += 1
                
                # Обновляем название если оно изменилось
                if category.label != name:
                    category.label = name
                    category.save()
                    
            except Category.DoesNotExist:
                # Создаем новую категорию с указанным UUID
                category = Category.objects.create(
                    pk=category_uuid,
                    label=name
                )
                self.statistics['categories_created'] += 1
            
            # Добавляем магазин к категории
            category.shops.add(shop)
            category_mapping[category_uuid] = category
        
        return category_mapping
    
    def process_parameters(self, parameters_data: Dict) -> Dict[str, Parameter]:
        """
        Обработка параметров товара
        Возвращает маппинг названий параметров на объекты Parameter
        """
        parameter_mapping = {}
        
        for param_name, param_value in parameters_data.items():
            parameter, created = Parameter.objects.get_or_create(
                label=param_name
            )
            
            if created:
                self.statistics['parameters_created'] += 1
            
            parameter_mapping[param_name] = parameter
        
        return parameter_mapping
    
    def process_product(
        self, 
        product_data: Dict, 
        category_mapping: Dict[str, Category],
        shop: Shop
    ) -> Optional[Product]:
        """
        Обработка одного товара
        """
        ext_id = product_data.get('id')
        if not ext_id:
            self.statistics['errors'].append("Товар пропущен: отсутствует внешний ID")
            return None
        
        category_uuid = product_data.get('category')
        category = category_mapping.get(category_uuid)
        
        if not category:
            self.statistics['errors'].append(
                f"Товар '{product_data.get('name', 'Unknown')}' (ext_id: {ext_id}) "
                f"пропущен: категория с UUID {category_uuid} не найдена"
            )
            return None
        
        # Подготовка данных для продукта
        product_defaults = {
            'category': category,
            'shop': shop,
        }
        
        # Маппинг полей
        for file_field, model_field in self.PRODUCT_FIELD_MAPPING.items():
            if file_field in product_data:
                product_defaults[model_field] = product_data[file_field]
        
        # Поиск или создание продукта
        product, created = Product.objects.update_or_create(
            ext_id=str(ext_id),
            shop=shop,
            defaults=product_defaults
        )
        
        if created:
            self.statistics['products_created'] += 1
        else:
            self.statistics['products_updated'] += 1
        
        return product
    
    def process_product_parameters(
        self, 
        product: Product, 
        parameters_data: Dict
    ):
        """
        Обработка параметров для конкретного товара
        """
        if not parameters_data:
            return
        
        parameter_mapping = self.process_parameters(parameters_data)
        
        for param_name, param_value in parameters_data.items():
            parameter = parameter_mapping[param_name]
            
            ProductParameter.objects.update_or_create(
                product=product,
                parameter=parameter,
                defaults={'value': str(param_value)}
            )
    
    @transaction.atomic
    def import_from_url(self, url: str) -> ImportResult:
        """
        Основной метод импорта товаров по URL
        """
        # Проверка URL
        is_valid, error_msg = self.validate_url(url)
        if not is_valid:
            return ImportResult(success=False, message=f"Неверный URL: {error_msg}")
        
        # Загрузка и парсинг YAML
        is_valid, data, error_msg = self.fetch_and_parse_yaml(url)
        if not is_valid:
            return ImportResult(success=False, message=error_msg)
        
        # Проверка структуры данных
        is_valid, error_msg = self.validate_data_structure(data)
        if not is_valid:
            return ImportResult(success=False, message=error_msg)
        
        try:
            # Получение или создание магазина
            self.shop, _ = Shop.objects.get_or_create(
                user=self.user,
                defaults={'label': data['shop']}
            )
            
            # Если магазин уже существовал, обновляем название если нужно
            if self.shop.label != data['shop']:
                self.shop.label = data['shop']
                self.shop.save()
            
            # Обработка категорий
            category_mapping = self.process_categories(data['categories'], self.shop)
            
            # Обработка товаров
            for product_data in data['goods']:
                product = self.process_product(product_data, category_mapping, self.shop)
                
                if product and 'parameters' in product_data:
                    self.process_product_parameters(product, product_data['parameters'])
            
            # Формирование результата
            return ImportResult(
                success=True,
                message="Импорт успешно завершен",
                shop_id=str(self.shop.id),
                products_created=self.statistics['products_created'],
                products_updated=self.statistics['products_updated'],
                categories_created=self.statistics['categories_created'],
                categories_found=self.statistics['categories_found'],
                errors=self.statistics['errors'] if self.statistics['errors'] else None
            )
            
        except Exception as e:
            error_msg = f"Критическая ошибка при импорте: {str(e)}"
            logger.exception(error_msg)
            return ImportResult(
                success=False,
                message=error_msg,
                errors=[error_msg]
            )