from django.urls import path

from oscar.core.application import OscarDashboardConfig
from oscar.core.loading import get_class


class PaymentsDashboardConfig(OscarDashboardConfig):
    label = "payments_dashboard"
    name = "oscar.apps.dashboard.payments"
    verbose_name = "Панель управления - Онлайн-оплата Yookassa"

    default_permissions = [
        "is_staff",
    ]

    # pylint: disable=attribute-defined-outside-init
    def ready(self):
        self.payments_list_view = get_class("dashboard.payments.views", "PaymentsListView")
        self.refunds_list_view = get_class("dashboard.payments.views", "RefundsListView")
        self.payment_detail_view = get_class("dashboard.payments.views", "PaymentDetailView")
        self.refund_detail_view = get_class("dashboard.payments.views", "RefundDetailView")
        #vlad
        self.update_sorce_view = get_class("dashboard.payments.views", "UpdateSourceView")
        self.delete_source_view = get_class("dashboard.payments.views", "DeleteSourceView")
        self.refund_transaction_view = get_class("dashboard.payments.views", "RefundTransactionView")
        self.add_source_view = get_class("dashboard.payments.views", "AddSourceView")
        self.add_transaction_view = get_class("dashboard.payments.views", "AddTransactionView")

    def get_urls(self):
        urls = [
            path("payments/", self.payments_list_view.as_view(), name="payments-list"),
            path("refunds/", self.refunds_list_view.as_view(), name="refunds-list"),
            path("payments/<str:pk>/", self.payment_detail_view.as_view(), name="payment-detail"),
            path("refunds/<str:pk>/", self.refund_detail_view.as_view(), name="refund-detail"),
            #vlad
            path(
                "payments/<int:pk>/refund/",
                self.refund_transaction_view.as_view(), 
                name='refund-transaction'
            ),
            path(
                "payments/<str:code>/refund/",
                self.refund_transaction_view.as_view(), 
                name='refund-transaction'
            ),
            path(
                "order/<str:number>/update-source/<int:pk>/",
                self.update_sorce_view.as_view(), 
                name='update-source'
            ),
            path(
                "order/<str:number>/delete-source/<int:pk>/",
                self.delete_source_view.as_view(), 
                name='delete-source'
            ),
            path(
                "order/<str:number>/add-source/",
                self.add_source_view.as_view(), 
                name='add-source'
            ),
            path(
                "order/<str:number>/add-transaction/",
                self.add_transaction_view.as_view(), 
                name='add-transaction'
            ),
        ]
        return self.post_process_urls(urls)
