import logging
from rest_framework import serializers
from django.contrib.auth.models import Group
from oscar.apps.customer.models import GroupEvotor
from oscar.apps.search.search_indexes import ProductIndex
from decimal import Decimal as D
from oscar.core.loading import get_model
from haystack import connections

logger = logging.getLogger("oscar.customer")

User = get_model("user", "User")
Staff = get_model("user", "Staff")
Store = get_model("store", "Store")
Product = get_model('catalogue', 'Product')
ProductClass = get_model('catalogue', 'ProductClass')
StockRecord = get_model("store", "StockRecord")
Category = get_model("catalogue", "Category")
AttributeOption = get_model("catalogue", "AttributeOption")
AttributeOptionGroup = get_model("catalogue", "AttributeOptionGroup")


class ProductSerializer(serializers.ModelSerializer):
    # товар
    id = serializers.CharField(source="evotor_id")
    name = serializers.CharField()
    article_number = serializers.CharField(source="article", required=False, allow_blank=True)
    description = serializers.CharField(
        source="short_description", required=False, allow_blank=True
    )
    parent_id = serializers.CharField(required=False, allow_blank=True, write_only=True)

    # класс товара
    type = serializers.CharField(write_only=True, required=False)
    measure_name = serializers.CharField(write_only=True, required=False)

    # товарная запись
    code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    store_id = serializers.CharField(write_only=True, required=False)
    price = serializers.CharField(write_only=True, required=False)
    cost_price = serializers.CharField(write_only=True, required=False)
    quantity = serializers.CharField(write_only=True, required=False)
    tax = serializers.CharField(write_only=True, required=False)
    allow_to_sell = serializers.BooleanField(write_only=True, required=False)

    updated_at = serializers.DateTimeField(write_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "code",
            "article_number",
            "description",
            "parent_id",
            "type",
            "measure_name",
            "store_id",
            "price",
            "cost_price",
            "quantity",
            "tax",
            "allow_to_sell",
            "updated_at",
        ]

    def create(self, validated_data):
        # Извлечение данных из validated_data
        parent_id = validated_data.pop("parent_id", None)
        measure_name = validated_data.pop("measure_name", None)
        store_id = validated_data.pop("store_id", None)
        price = validated_data.pop("price", None)
        cost_price = validated_data.pop("cost_price", None)
        quantity = validated_data.pop("quantity", None)
        tax = validated_data.pop("tax", None)
        allow_to_sell = validated_data.pop("allow_to_sell", None)
        code = validated_data.pop("code", None)

        type = validated_data.pop("type", None)
        updated_at = validated_data.pop("updated_at", None)

        evotor_id = validated_data.get("evotor_id")

        # Инициализация переменных
        parent_product = category = None

        # Обработка родительского товара или категории
        if parent_id:
            parent_product = self._get_parent_product(parent_id)
            category = self._get_or_create_category(parent_id)

        # Создание типа товара
        product_class = self._get_or_create_product_class(measure_name, quantity)

        # Создание или извлечение товара
        product = self._get_or_create_product(evotor_id, validated_data, parent_product, product_class)

        # Добавление категории, если она не существует
        if category:
            # Добавление категории к товару
            self._add_category_to_product(product, category)

        # Обновление родительского товара и структуры, если необходимо
        if parent_product:
            self._update_parent_product(product, parent_product)

        # Сохранение товара
        self._save(product)

        # Создание или извлечение партнера
        store = self._get_or_create_store(store_id)

        # Обработка товарной записи
        self._create_or_update_stock_record(product, store, code, price, cost_price, quantity, tax, allow_to_sell)

        return product

    def update(self, product, validated_data):
        # Извлечение данных из validated_data
        parent_id = validated_data.pop("parent_id", None)
        store_id = validated_data.pop("store_id", None)
        price = validated_data.pop("price", None)
        cost_price = validated_data.pop("cost_price", None)
        quantity = validated_data.pop("quantity", None)
        tax = validated_data.pop("tax", None)
        allow_to_sell = validated_data.pop("allow_to_sell", None)
        code = validated_data.pop("code", None)

        # Инициализация переменных
        parent_product = category = None

        # Обработка родительского товара или категории
        if parent_id:
            parent_product = self._get_parent_product(parent_id)
            category = self._get_or_create_category(parent_id)
        
        product.name = validated_data.get("name")
        product.article = validated_data.get("article")
        product.short_description = validated_data.get("short_description")

        # Добавление категории к товару
        if category:
            self._add_category_to_product(product, category)

        # Обновление родительского товара и структуры, если необходимо
        if parent_product:
            self._update_parent_product(product, parent_product)

        # Сохранение товара
        self._save(product)

        # Создание или извлечение партнера
        store = self._get_or_create_store(store_id)

        # Обработка товарной записи
        self._create_or_update_stock_record(product, store, code, price, cost_price, quantity, tax, allow_to_sell)

        return product
    
    def _save(self, product):
        product.save()
        search_backend = connections['default'].get_backend()
        search_backend.update(ProductIndex(), [product])

    def _get_parent_product(self, parent_id):
        """Обработка родительского товара или категории"""
        try:
            parent_product = Product.objects.get(evotor_id=parent_id)
            parent_product.structure = Product.PARENT
            parent_product.save()
            return parent_product
        except Product.DoesNotExist:
            return None

    def _get_or_create_product_class(self, measure_name, quantity):
        """Создание или извлечение класса товара"""
        return ProductClass.objects.get_or_create(
            name="Тип товара Эвотор",
            defaults={
                "track_stock": bool(quantity),
                "requires_shipping": False,
                "measure_name": measure_name,
            }
        )[0]

    def _get_or_create_product(self, evotor_id, validated_data, parent_product, product_class):
        """Создание или извлечение товара"""
        return Product.objects.get_or_create(
            evotor_id=evotor_id,
            defaults={
                "structure": Product.STANDALONE if not parent_product else Product.CHILD,
                "product_class": product_class,
                "is_public": True,
                "parent": parent_product,
                **validated_data
            }
        )[0]
    
    def _get_or_create_category(self, evotor_id):
        """Создание или извлечение категории"""
        try:
            cat = Category.objects.get(
                evotor_id=evotor_id,
            )
        except Category.DoesNotExist:
            cat = Category.add_root(name=f"Категория {evotor_id}", evotor_id=evotor_id)

        return cat

    def _add_category_to_product(self, product, category):
        """Добавление категории к товару"""
        product.categories.add(category)

    def _update_parent_product(self, product, parent_product):
        """Обновление родительского товара и структуры"""
        product.parent_product = parent_product
        product.structure = Product.CHILD

    def _get_or_create_store(self, store_id):
        """Создание или извлечение партнера"""
        return Store.objects.get_or_create(evotor_id=store_id)[0]

    def _create_or_update_stock_record(self, product, store, code, price, cost_price, quantity, tax, allow_to_sell):
        """Создание или обновление товарной записи"""
        stockrecord, created = StockRecord.objects.get_or_create(
            product=product,
            store_id=store.id,
            defaults={
                "product": product,
                "store": store,
                "evotor_code": code if code else "site-%s" % product.id,
                "price": D(price),
                "cost_price": D(cost_price),
                "is_public": allow_to_sell,
                "num_in_stock": int(quantity),
                "tax": tax,
            },
        )

        if created:
            stockrecord.save()
        else:
            stockrecord.price = D(price)
            stockrecord.cost_price = D(cost_price)
            stockrecord.is_public = allow_to_sell
            stockrecord.num_in_stock = int(quantity)
            stockrecord.tax = tax
            stockrecord.save()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:     
            store_id = self.context.get("store_id", None)
            
            representation["measure_name"] = instance.get_product_class().measure_name

            parent_id = instance.get_evotor_parent_id()
            if parent_id:
                representation["parent_id"] = parent_id
            
            stc = StockRecord.objects.filter(product=instance, store__evotor_id=store_id).first()

            if stc:
                representation["code"] = stc.evotor_code
                representation["price"] = stc.price
                representation["cost_price"] = stc.cost_price
                representation["quantity"] = stc.num_in_stock
                representation["tax"] = stc.tax
                representation["allow_to_sell"] = stc.is_public

        except Exception as e:
            logger.error(f"Ошибка определения товара: {e}")
            representation["measure_name"] = "шт"
            representation["tax"] = "NO_VAT"
            representation["allow_to_sell"] = False
            representation["price"] = 0
            representation["cost_price"] = 0
            representation["quantity"] = 0

        representation["type"] = "NORMAL"

        if not representation.get("id"):
            representation.pop("id", None)

        return representation


class ProductsSerializer(serializers.ModelSerializer):
    items = ProductSerializer(many=True)

    class Meta:
        model = Product
        fields = ["items"]

    def create(self, validated_data):    
        items_data = validated_data.get("items", [])
        store_id = self.context.get("store_id", None)
        return [ProductSerializer(context={"store_id": store_id}).create(item_data) for item_data in items_data]

    def update(self, instances, validated_data):
        items_data = validated_data.get('items', [])
        store_id = self.context.get("store_id", None)
        products = []

        for item_data in items_data:
            try:
                product_instance = instances.get(evotor_id=item_data['id'])  # `instance` — это QuerySet
                product = ProductSerializer(context={"store_id": store_id}).update(product_instance, item_data)
            except Product.DoesNotExist:
                continue  # Пропускаем, если объект не найден

            products.append(product)

        return products


class ProductGroupSerializer(serializers.ModelSerializer):
    # категория / товар
    id = serializers.CharField(source="evotor_id")
    name = serializers.CharField()
    parent_id = serializers.CharField(write_only=True, required=False, allow_blank=True)

    # только у родительского товара
    attributes = serializers.CharField(write_only=True, required=False)

    updated_at = serializers.DateTimeField(write_only=True)

    class Meta:
        model = None
        fields = [
            "id",
            "name",
            "parent_id",
            "attributes",
            "updated_at",
        ]

    def create(self, validated_data):
        """
            {
            "parent_id": "1ddea16b-971b-dee5-3798-1b29a7aa2e27",
            "name": "Группа",
            "barcodes": [
                "2000000000060"
            ],
            "attributes": [
                {
                "id": "36755a25-8f56-11e8-96a6-85f64fd5f8e3",
                "name": "Цвет",
                "choices": [
                    {
                    "id": "36755a27-8f56-11e8-96a6-85f64fd5f8e3",
                    "name": "Зелёный"
                    }
                ]
                }
            ]
            }
        """
        evotor_id = validated_data.get("evotor_id")

        attributes = validated_data.pop("attributes", None)
        parent_id = validated_data.pop("parent_id", None)
        updated_at = validated_data.pop("updated_at", None)
        
        if attributes:
            self.Meta.model = Product
            product_class = self._get_or_create_product_class()
            instance = Product.objects.get_or_create(
                evotor_id=evotor_id,
                defaults={
                    "structure": Product.PARENT,
                    "product_class": product_class,
                    "is_public": True,
                    **validated_data
                }
            )[0]

            category = self._get_or_create_category(parent_id)
            attr_group = self._get_or_create_attr_group(attributes)

            instance.categories.add(category)
            instance.attributes.add(attr_group)
        else:
            self.Meta.model = Category
            if parent_id:
                parent = self._get_or_create_category(parent_id)
                instance = parent.add_child(
                    evotor_id=evotor_id,
                    **validated_data
                )
            else:
                instance = self._get_or_create_category(evotor_id)

        return instance

    def update(self, instance, validated_data):
        """
            {
            "parent_id": "1ddea16b-971b-dee5-3798-1b29a7aa2e27",
            "name": "Группа",
            "barcodes": [
                "2000000000060"
            ],
            "attributes": [
                {
                "id": "36755a25-8f56-11e8-96a6-85f64fd5f8e3",
                "name": "Цвет",
                "choices": [
                    {
                    "id": "36755a27-8f56-11e8-96a6-85f64fd5f8e3",
                    "name": "Зелёный"
                    }
                ]
                }
            ]
            }
        """
        name = validated_data.get("name", None)
        attributes = validated_data.pop("attributes", None)
        parent_id = validated_data.pop("parent_id", None)
        updated_at = validated_data.pop("updated_at", None)
        
        if attributes:
            self.Meta.model = Product

            category = self._get_or_create_category(parent_id)
            attr_group = self._get_or_create_attr_group(attributes)
            
            instance.name = name
            instance.structure = Product.PARENT
            instance.categories.add(category)
            instance.attributes.add(attr_group)

            instance.save()
        else:
            self.Meta.model = Category

            if parent_id:
                parent = self._get_or_create_category(parent_id)
                if instance.parent != parent:
                    instance.move(parent, pos="last-child")

            instance.name = name
            instance.save()

        return instance

    def to_representation(self, instance):
        if isinstance(instance, Product):#
            self.Meta.model = Product
            representation = super().to_representation(instance)
            try:
                attribute_values = instance.attribute_values.filter(is_variant=True)
                representation["attributes"] = [
                    {
                        **({"id": attribute_value.attribute.evotor_id} if attribute_value.attribute.evotor_id else {}),
                        "name": attribute_value.attribute.name,
                        "choices": [
                            {
                                **({"id": choice.evotor_id} if choice.evotor_id else {}),
                                "name": choice.option
                            }
                            for choice in attribute_value.value.all()
                        ]
                        if attribute_value.value else []
                    }
                    for attribute_value in attribute_values
                ]

            except Exception as e:
                logger.error(f"Ошибка определения списка магазинов сотрудника: {e}")
                representation["attributes"] = []
        else:
            self.Meta.model = Category
            representation = super().to_representation(instance)

        if not representation.get("id"):
            representation.pop("id", None)

        return representation

    def _get_or_create_product_class(self):
        """Создание или извлечение класса товара"""
        return ProductClass.objects.get_or_create(
            name="Тип товара Эвотор",
            defaults={
                "track_stock": True,
                "requires_shipping": False,
                "measure_name": "шт",
            }
        )[0]
    
    def _get_or_create_category(self, evotor_id):
        """Создание или извлечение категории"""
        try:
            cat = Category.objects.get(
                evotor_id=evotor_id,
            )
        except Category.DoesNotExist:
            cat = Category.add_root(name=f"Категория {evotor_id}", evotor_id=evotor_id)

        return cat
    
    def _get_or_create_attr_group(self, attributes):
        """
        "attributes": [
            {
            "id": "36755a25-8f56-11e8-96a6-85f64fd5f8e3",
            "name": "Цвет",
            "choices": [
                {
                "id": "36755a27-8f56-11e8-96a6-85f64fd5f8e3",
                "name": "Зелёный"
                }
            ]
            }
        ]
        """
        group = None
        for attribute in attributes:
            group = AttributeOptionGroup.objects.get_or_create(
                evotor_id=attribute["id"],
                defaults={"name": attribute["name"]}
            )[0]

            for choice in attribute.get("choices", []):
                AttributeOption.objects.get_or_create(
                    evotor_id=choice["id"],
                    group=group,
                    defaults={"option": choice["name"]}
                )

        return group


class ProductGroupsSerializer(serializers.ModelSerializer):
    items = ProductGroupSerializer(many=True)

    class Meta:
        model = Category
        fields = ["items"]
    
    def create(self, validated_data):    
        items_data = validated_data.get("items", [])
        store_id = self.context.get("store_id", None)
        return [ProductGroupSerializer(context={"store_id": store_id}).create(item_data) for item_data in items_data]

    def update(self, instances, validated_data):
        items_data = validated_data.get('items', [])
        store_id = self.context.get("store_id", None)
        product_groups = []

        for item_data in items_data:
            try:
                product_group_instance = instances.get(evotor_id=item_data['id'])  # `instance` — это QuerySet
                product_group = ProductGroupSerializer(context={"store_id": store_id}).update(product_group_instance, item_data)
            except Product.DoesNotExist:
                continue  # Пропускаем, если объект не найден

            product_groups.append(product_group)

        return product_groups
    