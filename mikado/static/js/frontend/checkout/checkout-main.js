var address_fields = document.getElementById('address_fields');
var submit_btn = document.getElementById('submit_order');

var checkout_errors = document.querySelector('[data-id="checkout-error-list"]');
var error_address = checkout_errors.querySelector('[data-error="address"]');
var error_flat = checkout_errors.querySelector('[data-error="flat"]');
var error_enter = checkout_errors.querySelector('[data-error="enter"]');
var error_floor = checkout_errors.querySelector('[data-error="floor"]');
var error_amount = checkout_errors.querySelector('[data-error="amount"]');

var amountValid = true;
var addressValid = true;

var order_time = document.getElementById('id_order_time');
var delivery_time_btn = document.querySelectorAll('[data-id="delivery-time"]');
var delivery_time_later = document.getElementById('delivery_time_later');

var shipping_method_buttons = document.querySelectorAll('[data-id="delivery-method-button"]');
var delivery_method_block = document.querySelector('[data-id="delivery-method-block"]');
var delivery_time_block = document.querySelector('[data-id="delivery-time-block"]');
var time_title = document.querySelector('[data-id="order-time-title"]');

var checkout_totals = document.getElementById('checkout_totals');
var checkout_fields = document.querySelectorAll('[data-id="v-input-field"]');
var textares = document.querySelectorAll('textarea');
var payment_method = document.getElementById('id_payment_method');
var line2 = document.querySelector('#id_line2');
var line3 = document.querySelector('#id_line3');
var line4 = document.querySelector('#id_line4');
var email_block = document.querySelector('[data-field="v-email-field"]');
var email_field = email_block.querySelector('#email_field_label');

const OFFLINE_PAYMENT = ['CASH'];
const ONLINE_PAYMENT = ['SBP', 'CARD'];
const baseURL = window.location.origin;


// Инициализация адреса
document.addEventListener('DOMContentLoaded', function () {
    var addressInital = line1.value;
    if (addressInital) {
        line1.readOnly = true;
        line1.setAttribute('captured', true);
        createMap(addressInital);
    }
    validateCheckout();
    textares.forEach(function(textarea) {
        if (textarea.scrollHeight < 77) {
            textarea.style.height = textarea.scrollHeight + 'px';
        } else {
            textarea.style.height = '77px';
        }
    });
});

// Смена метода доставки
shipping_method_buttons.forEach(function(button) {
    button.addEventListener('click', function() {
        shippingMethod = this.value;
        shipping_method.value = shippingMethod;
        let leftPosition = this.getBoundingClientRect().left - this.parentElement.getBoundingClientRect().left;
        delivery_method_block.style.left = `${leftPosition}px`;
        GetTime({address: line1.value, coords: [lon.value, lat.value], shippingMethod: shippingMethod}).then(function(result) {
            timeCaptured(result);
        });
        if (shippingMethod === "self-pick-up") {
            address_fields.classList.add('d-none');
            time_title.innerHTML = 'Время самовывоза';
        } else {
            address_fields.classList.remove('d-none');
            time_title.innerHTML = 'Время доставки';
        }
        getNewTotals(shippingMethod);
    });
});

// Выбрана доставка "самовывоз как можно скорее"
delivery_time_btn.forEach(function(time_btn) {
    time_btn.addEventListener('click', function() {
        let leftPosition = time_btn.getBoundingClientRect().left - time_btn.parentElement.getBoundingClientRect().left;
        delivery_time_block.style.left = `${leftPosition}px`;

        var delivery_time_method = time_btn.getAttribute("data-type");
        if (delivery_time_method === "now") {
            GetTime({address: line1.value, coords: [lon.value, lat.value], shippingMethod: shippingMethod}).then(function(result) {
                order_time.value = result.timeUTC;
                timeCaptured(result);
            });
            delivery_time.classList.remove('hidden');
            delivery_time.classList.add('active');
            delivery_time_later.classList.add('hidden');
            delivery_time_later.classList.remove('active');
        } else {
            delivery_time_later.classList.remove('hidden');
            delivery_time_later.classList.add('active');
            delivery_time.classList.add('hidden');
            delivery_time.classList.remove('active');
        }
    });
});

// Обновление итогов
function getNewTotals(selectedMethod, zonaId = null) {
    console.log('getNewTotals');

    // Формируем параметры запроса в URL
    const url = new URL(url_update_totals, baseURL); 
    url.searchParams.append('shipping_method', selectedMethod);
    // if (zonaId) {
        url.searchParams.append('zona_id', zonaId);
    // }


    fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 202) {
            checkout_totals.innerHTML = data.totals;
            error_amount.innerHTML = data.min_order;
        }
    })
    .finally(() => {
        validateCheckout();
    });
}

// Сдача или чек
payment_method.addEventListener('change', function() {
    if (OFFLINE_PAYMENT.includes(this.value)) {
        email_field.innerHTML = 'Нужна сдача с ...';
        email_block.classList.remove('d-none-i');
    } else if (ONLINE_PAYMENT.includes(this.value)) {
        email_field.innerHTML = 'E-mail для получения чеков';
        email_block.classList.remove('d-none-i');
    } else {
        email_block.classList.add('d-none-i');
    }
});

// Лейблы при заполнении текста
checkout_fields.forEach(function(wrapper) {
    var input_field = wrapper.querySelector('.v-input');
    if (input_field.value !== "") {
        wrapper.classList.add('v-input__label-active');
    }
    input_field.addEventListener('focusin', function() {
        wrapper.classList.add('v-input__label-active');
    });
    input_field.addEventListener('focusout', function() {
        if (input_field.value === "") {
            wrapper.classList.remove('v-input__label-active');
        }
        validateAddress();
        checkValid();
    });
});

// Авторасширение текстовых полей
textares.forEach(function(textarea) {
    textarea.addEventListener('input', function() {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    });
    textarea.addEventListener('scroll', function() {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    });
});

// Не отправлять форму enter-ом
document.getElementById('place_order_form').addEventListener('keypress', function(event) {
    if (event.which === 13) {
        event.preventDefault();
    }
});

function validate() {
    validateCheckout();
}

// Валидация по мин заказу и адресу
function validateCheckout() {
    console.log('validateCheckout');
    validateAddress();
    validateTotals();
    checkValid();
}

function checkValid() {
    console.log('checkValid');
    if (amountValid && addressValid) {
        console.log('checkValid VALID');
        submit_btn.disabled = false;
        checkout_errors.classList.add('d-none');
    } else {
        console.log('checkValid NO VALID');
        submit_btn.disabled = true;
        checkout_errors.classList.remove('d-none');    
    }
}

// Валидация по адресу
function validateAddress() {
    addressValid = true;
    shippingMethod = shipping_method.value;
    if (shippingMethod === "zona-shipping") {
        if (!line1.value || line1.getAttribute('captured') === "false" || line1.getAttribute('valid') === "false") {
            addressValid = false;
            error_address.classList.remove('d-none');
            line1_container.classList.add("not-valid");
        } else {
            error_address.classList.add('d-none');
            line1_container.classList.remove("not-valid");
        }

        if (line2.value > 1000 || line2.value < 1) {
            addressValid = false;
            error_flat.classList.remove('d-none');
            line2.classList.add("not-valid");
        } else {
            error_flat.classList.add('d-none');
            line2.classList.remove("not-valid");
        }

        if (line3.value > 100 || line3.value < 1) {
            addressValid = false;
            error_enter.classList.remove('d-none');
            line3.classList.add("not-valid");
        } else {
            error_enter.classList.add('d-none');
            line3.classList.remove("not-valid");
        }

        if (line4.value > 100 || line4.value < 1) {
            addressValid = false;
            error_floor.classList.remove('d-none');
            line4.classList.add("not-valid");
        } else {
            error_floor.classList.add('d-none');
            line4.classList.remove("not-valid");
        }
    }
}

// Валидация по сумме заказа
function validateTotals() {
    amountValid = true;
    if (checkout_totals.querySelector('[data-min-order]').getAttribute("data-min-order") === "false" && shippingMethod === "zona-shipping") {
        amountValid = false;
        error_amount.classList.remove('d-none');
    } else {
        error_amount.classList.add('d-none');
    }
}

// Начисляем стоимость доставки в зависимости от зоны
function shippingCharge(zonaId = null) {
    console.log("ShippingCharge");
    getNewTotals(shippingMethod, zonaId);
}

// Loading spinner
submit_btn.addEventListener('click', function() {
    this.classList.add('sending');
});

// Таймер обновления времени доставки к адресу каждые 5 минут
function updateTimes() {
    setInterval(function() {
        console.log('upd timer');
        GetTime({adrs: line1.value, shippingMethod: shippingMethod}).then(function(result) {
            timeCaptured(result);
        });
    }, 300000);
}
updateTimes();

