from decimal import Decimal as D
from rest_framework import serializers

from django.conf import settings
from django.utils.timezone import now

from oscar.core.loading import get_model

User = get_model("user", "User")
Store = get_model("store", "Store")
Product = get_model("catalogue", "Product")
Additional = get_model("catalogue", "Additional")
ProductClass = get_model("catalogue", "ProductClass")
StockRecord = get_model("store", "StockRecord")
Order = get_model("order", "Order")
OrderNote = get_model("order", "OrderNote")
OrderDiscount = get_model("order", "OrderDiscount")
OrderLineDiscount = get_model("order", "OrderLineDiscount")
Line = get_model("order", "Line")
LinePrice = get_model("order", "LinePrice")
Source = get_model("payment", "Source")
SourceType = get_model("payment", "SourceType")
Transaction = get_model("payment", "Transaction")

# ========== Сериализоторы для Мобильного кассира ==========


class OrderLineSerializer(serializers.Serializer):
    id = serializers.CharField(source="article")
    product_id = serializers.CharField()
    code = serializers.CharField(source="evotor_code")
    quantity = serializers.IntegerField()
    result_sum = serializers.DecimalField(
        source="line_price", max_digits=12, decimal_places=2
    )
    sum = serializers.DecimalField(
        source="line_price_before_discounts", max_digits=12, decimal_places=2
    )
    price = serializers.DecimalField(
        source="unit_price", max_digits=12, decimal_places=2
    )
    tax = serializers.DictField()
    position_discount = serializers.DictField(required=False)

    class Meta:
        model = Line
        fields = (
            "id",
            "product_id",
            "code",
            "quantity",
            "result_sum",
            "sum",
            "price",
            "tax",
            "position_discount",
        )

    def create(self, validated_data, order, store):
        product, created = Product.objects.get_or_create(
            evotor_id=validated_data["product_id"],
            defaults={
                "name": "Несозданый продукт",
                "product_class": self._get_or_create_product_class(),
            },
        )
        if created:
            stockrecord = StockRecord.objects.get_or_create(
                product=product,
                store_id=store.id,
                defaults={
                    "product": product,
                    "store": store,
                    "evotor_code": "site-%s" % product.id,
                    "price": D(validated_data["price"]),
                },
            )[0]
        else:
            stockrecord = product.stockrecords.filter(
                store__evotor_id=store.evotor_id, is_public=True
            ).first()
        line = Line.objects.create(
            order=order,
            store=store,
            name=product.get_name(),
            store_name=store.name,
            evotor_code=validated_data["code"],
            product=product,
            stockrecord=stockrecord,
            quantity=validated_data["quantity"],
            article=validated_data["id"],
            status="Завершён",
            line_price=validated_data["result_sum"],
            line_price_before_discounts=validated_data["sum"],
            unit_price=validated_data["price"],
            tax_code=validated_data["tax"]["type"],
        )
        LinePrice.objects.create(
            order=order,
            line=line,
            quantity=line.quantity,
            price=line.line_price,
            tax_code=line.tax_code,
        )

        position_discount = validated_data.get("position_discount", None)
        if position_discount:
            discount_amount = position_discount.get("discount_sum", 0)
            order_discount = OrderDiscount.objects.filter(order=order).first()
            if not order_discount:
                order_discount = OrderDiscount.objects.create(
                    order=order,
                    message="Скидка сотрудником позицию заказа",
                    amount=discount_amount,
                    frequency=1,
                    voucher_code=position_discount.get("coupon") or "",
                )
            else:
                order_discount.amount += discount_amount
                order_discount.frequency += 1
                order_discount.save()

            line.discounts.create(
                order_discount=order_discount,
                amount=discount_amount,
            )

    def _get_or_create_product_class(self):
        """Создание или извлечение класса товара"""
        return ProductClass.objects.get_or_create(
            name="Тип товара Эвотор",
            defaults={
                "track_stock": True,
                "requires_shipping": False,
                "measure_name": "шт",
            },
        )[0]

    def to_representation(self, instance):
        return {
            "type": "NORMAL",
            "code": instance.evotor_code,
            "commodity_id": instance.product.evotor_id,
            "name": instance.get_full_name(),
            "measureName": instance.product.get_product_class().measure_name,
            "quantity": instance.quantity,
            "tax": instance.tax_code,
            "price": instance.line_price_before_discounts,
            "priceWithDiscount": instance.line_price,
            "sub_positions": [
                {
                    "type": "NORMAL",
                    "commodity_id": additional.additional.evotor_id,
                    "name": additional.additional.name,
                    "measureName": "шт",
                    "quantity": additional.value,
                    "tax": additional.additional.tax,
                    "price": additional.additional.price,
                }
                for additional in instance.attributes.filter(additional__isnull=False)
            ],
        }


class OrderDiscountSerializer(serializers.Serializer):
    discount_sum = serializers.DecimalField(
        source="amount", max_digits=12, decimal_places=2
    )
    coupon = serializers.CharField(source="voucher_code", required=False)

    class Meta:
        model = OrderDiscount
        fields = ("discount_sum", "coupon")

    def create(self, validated_data, order):
        OrderDiscount.objects.create(
            order=order,
            message="Скидка сотрудником на весь заказ",
            amount=validated_data["discount_sum"],
            voucher_code=validated_data.get("coupon") or "",
        )


class PaymentSerializer(serializers.Serializer):
    id = serializers.CharField(source="code")
    type = serializers.CharField(source="source_type")
    sum = serializers.DecimalField(source="amount", max_digits=12, decimal_places=2)
    app_info = serializers.DictField(source="reference")
    parts = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = Source
        fields = ("id", "type", "sum", "app_info", "parts")

    def create(self, validated_data, order):
        source_type, _ = SourceType.objects.get_or_create(
            name=validated_data["app_info"]["name"]
        )
        amount_debited = sum(
            D(part["part_sum"]) - D(part["change"])
            for part in validated_data.get("parts", [])
        )
        source = Source.objects.create(
            order=order,
            source_type=source_type,
            amount_allocated=amount_debited,
            amount_debited=amount_debited,
            reference=validated_data["type"],
            refundable=False,
            paid=True,
        )
        Transaction.objects.create(
            source=source,
            txn_type="Payment",
            amount=amount_debited,
            reference="Эвотор",
            status="succeeded",
            paid=True,
            refundable=False,
            receipt=True,
        )

    def update(self, validated_data, order, type):
        source_type, _ = SourceType.objects.get_or_create(
            name=validated_data["app_info"]["name"]
        )

        amount_debited = D(0)
        amount_refunded = D(0)

        if type == "SELL":
            amount_debited = sum(
                D(part["part_sum"]) - D(part["change"])
                for part in validated_data.get("parts", [])
            )
        else:
            amount_refunded = sum(
                D(part["part_sum"]) - D(part["change"])
                for part in validated_data.get("parts", [])
            )

        source, _ = Source.objects.get_or_create(
            order=order,
            source_type=source_type,
            defaults={
                "amount_debited": amount_debited,
                "amount_refunded": amount_refunded,
                "reference": validated_data["type"],
            },
        )

        if type == "SELL":
            source.amount_debited += amount_debited
        else:
            source.amount_refunded += amount_refunded

        source.paid = source.balance >= source.amount_allocated
        source.refundable = source.transactions.filter(refundable=True).exists()

        source.save()

        txn_type = "Payment" if type == "SELL" else "Refund"

        transaction, _ = Transaction.objects.get_or_create(
            source=source,
            txn_type=txn_type,
            defaults={
                "amount": amount_debited if type == "SELL" else amount_refunded,
                "reference": "Эвотор",
                "status": "succeeded",
                "paid": True if type == "SELL" else False,
                "refundable": False,
                "receipt": True,
            },
        )

        transaction.amount = amount_debited if type == "SELL" else amount_refunded
        transaction.paid = True if type == "SELL" else False
        transaction.save()


class OrderSerializer(serializers.Serializer):
    id = serializers.CharField(source="evotor_id")
    type = serializers.CharField(write_only=True)
    number = serializers.IntegerField(write_only=True)
    store_id = serializers.CharField(write_only=True)
    created_at = serializers.DateTimeField(write_only=True)
    extras = serializers.DictField(write_only=True, required=False)
    body = serializers.DictField(write_only=True)

    class Meta:
        model = Order
        fields = ("id", "number", "store_id", "created_at", "extras", "body")

    def create(self, validated_data):
        evotor_id = validated_data.get("evotor_id")
        number = validated_data.get("number")
        store_id = validated_data.get("store_id")
        body = validated_data.get("body")
        extras = validated_data.get("extras", None)
        type = validated_data.pop("type", None)

        store = Store.objects.get(evotor_id=store_id)

        order = Order.objects.create(
            number=(900000 + number),
            evotor_id=evotor_id,
            site="Эвотор",
            store=store,
            total=body.get("result_sum", 0),
            shipping_method="Самовывоз",
            status=(
                settings.OSCAR_SUCCESS_ORDER_STATUS
                if type == "SELL"
                else settings.OSCAR_FAIL_ORDER_STATUS
            ),
            date_finish=now(),
            order_time=now(),
        )

        if extras:
            OrderNote.objects.create(
                order=order,
                note_type=OrderNote.STAFF,
                message=str(extras),
            )

        positions = body.get("positions", [])
        for position in positions:
            if position.get("parent_id", None) != Additional.parent_id:
                OrderLineSerializer().create(position, order, store)

        order_lines = order.lines.all()
        for position in positions:
            if position.get("parent_id", None) == Additional.parent_id:
                additional = Additional.objects.get_or_create(
                    evotor_id=position.get("product_id"),
                    defaults={
                        "name": "Несозданый продукт",
                        "price": position.get("price"),
                    },
                )[0]
                added = False
                for line in order_lines:
                    product = line.product
                    if additional in product.get_product_additionals():
                        line.attributes.create(
                            additional=additional, value=position.get("quantity")
                        )
                        added = True
                if not added:
                    line.attributes.create(
                        additional=additional, value=position.get("quantity")
                    )

        discounts = body.get("doc_discounts", [])
        for discount in discounts:
            OrderDiscountSerializer().create(discount, order)

        payments = body.get("payments", [])
        for payment in payments:
            PaymentSerializer().create(payment, order)

        return order

    def update(self, instance, validated_data):
        store_id = validated_data.get("store_id")
        body = validated_data.get("body")
        type = validated_data.pop("type", None)

        store = Store.objects.get(evotor_id=store_id)

        msg = "Коррекция продажи"

        if type == "PAYBACK":
            msg = "Коррекция возврата"
            instance.set_status(settings.OSCAR_FAIL_ORDER_STATUS)

        OrderNote.objects.create(
            order=instance,
            note_type=OrderNote.SYSTEM,
            message=f"Заказ обновлен. {msg}. Сообщение: {body.get('reason', '-')}",
        )

        self._delete_old_data(instance)

        positions = body.get("positions", [])
        for position in positions:
            if position.get("parent_id", None) != Additional.parent_id:
                OrderLineSerializer().create(position, instance, store)

        order_lines = instance.lines.all()
        for position in positions:
            if position.get("parent_id", None) == Additional.parent_id:
                additional = Additional.objects.get_or_create(
                    evotor_id=position.get("product_id"),
                    defaults={
                        "name": "Несозданый продукт",
                        "price": position.get("price"),
                    },
                )[0]
                added = False
                for line in order_lines:
                    product = line.product
                    if additional in product.get_product_additionals():
                        line.attributes.create(
                            additional=additional, value=position.get("quantity")
                        )
                        added = True
                if not added:
                    line.attributes.create(
                        additional=additional, value=position.get("quantity")
                    )

        discounts = body.get("doc_discounts", [])
        for discount in discounts:
            OrderDiscountSerializer().create(discount, instance)

        payments = body.get("payments", [])
        for payment in payments:
            PaymentSerializer().update(payment, instance, type)

        return instance

    def _delete_old_data(self, order):
        old_lines = order.lines.all()
        for old_line in old_lines:
            old_line.delete()

        old_discounts = OrderDiscount.objects.filter(
            order=order,
        )
        for old_discount in old_discounts:
            old_discount.delete()

    def to_representation(self, instance):
        paid = 0
        for src in instance.sources.all():
            paid += src.amount_debited - src.amount_refunded

        representation = {
            "client_phone": str(instance.user.username) if instance.user else "",
            "client_email": instance.user.email if instance.user else "",
            "should_print_receipt": False,
            "editable": False if paid else True,
            "payment_type": (
                instance.sources.last().reference if instance.sources.exists() else None
            ),
            "receiptDiscount": instance.total_discount,
            "extra": {
                "Номер заказа": instance.number,
                "Время заказа": instance.order_time,
                "Оплата": f"{paid}₽" if paid > 0 else "Нет",
                "Доставка": instance.shipping_method,
            },
            "positions": [
                OrderLineSerializer(line).data for line in instance.lines.all()
            ],
        }

        notes = instance.notes.values_list("note_type", "message")
        if notes.exists():
            representation["note"] = ", ".join(
                f"{note_type}: {message}" for note_type, message in notes
            )

        return representation
