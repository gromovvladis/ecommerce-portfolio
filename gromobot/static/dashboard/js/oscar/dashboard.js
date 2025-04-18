/*global jQuery */

var dashboard = (function (o, $) {

    function onFileChange(evt) {
        var reader = new FileReader();
        var imgId = evt.target.id + "-image";
        reader.onload = (function () {
            return function (e) {
                var imgDiv = $("#" + imgId);
                imgDiv.children('img').attr('src', e.target.result);
            };
        })();
        reader.readAsDataURL(evt.target.files[0]);

        var $input = $(evt.target);
        var $parentTab = $input.parents('.tab-pane').first();
        var imageContainer = $input.parents('.sortable-handle').first();
        imageContainer.find('.btn-reorder').removeAttr('disabled').removeClass('disabled');
        imageContainer.removeClass('sortable-disabled');
        var $extraImg = $input.parents('.upload-image').children('tr').last();
        var $totalForms = $parentTab.find("input[name$=images-TOTAL_FORMS]");
        var $maxForms = $parentTab.find("input[name$=images-MAX_NUM_FORMS]");
        var numExisting = parseInt($totalForms.val());
        var numMax = parseInt($maxForms.val());

        // Do not create extra image form if number of maximum allowed forms has reached.
        if (numExisting < numMax) {
            var $newImg = o.dashboard._extraProductImg.clone();
            var productId = $('#images-0-product').val();
            $newImg.insertAfter($extraImg);
            // update attrs on cloned el
            $newImg.find("[id^='id_images-']," +
                "[for^='id_images-']," +
                "[id^='upload_button_id_images-']," +
                "img[alt='thumbnail']").each(function () {
                    var $el = $(this);
                    ["id", "name", "for", "onload", "onerror"].forEach(function (attr) {
                        var val = $el.attr(attr);
                        if (val) {
                            var parts = val.split('-');
                            parts[1] = numExisting;
                            $el.attr(attr, parts.join('-'));
                        }
                    });
                });
            $newImg.find('#id_images-' + numExisting + '-display_order').val(numExisting);
            $newImg.find('#id_images-' + numExisting + '-product').val(productId);

            var $newFile = $newImg.find('input[type="file"]');
            $newFile.change(onFileChange);
            numExisting += 1;
            $totalForms.val(numExisting);
        }
    }

    o.getCsrfToken = function () {
        // Extract CSRF token from cookies
        var cookies = document.cookie.split(';');
        var csrf_token = null;
        $.each(cookies, function (index, cookie) {
            var cookieParts = $.trim(cookie).split('=');
            if (cookieParts[0] == 'csrftoken') {
                csrf_token = cookieParts[1];
            }
        });
        // Extract from cookies fails for HTML-Only cookies
        if (!csrf_token) {
            csrf_token = $(document.forms.valueOf()).find('[name="csrfmiddlewaretoken"]')[0].value;
        }
        return csrf_token;
    };

    o = {
        init: function (options) {
            // Run initialisation that should take place on every page of the dashboard.
            var defaults = {
                'dateFormat': 'DD/MM/YYYY',
                'timeFormat': 'HH:mm',
                'datetimeFormat': 'DD/MM/YYYY HH:mm',
                'stepMinute': 15,
                'datetimePickerConfig': {
                    icons: {
                        time: 'fas fa-clock',
                        date: 'fas fa-calendar',
                        up: 'fas fa-arrow-up',
                        down: 'fas fa-arrow-down',
                        previous: 'fas fa-chevron-left',
                        next: 'fas fa-chevron-right',
                        today: 'fas fa-calendar-check-o',
                        clear: 'fas fa-trash',
                        close: 'fas fa-times'
                    }
                },
                'tinyConfig': {
                    entity_encoding: 'raw',
                    statusbar: false,
                    menubar: false,
                    plugins: "link lists",
                    style_formats: [
                        { title: 'Text', block: 'p' },
                        { title: 'Heading', block: 'h2' },
                        { title: 'Subheading', block: 'h3' }
                    ],
                    toolbar: "styles | bold italic blockquote | bullist numlist | link"
                }
            };
            o.dashboard.options = $.extend(true, defaults, options);

            o.dashboard.initWidgets(window.document);
            o.dashboard.initForms();

            $(".category-select ul").prev('a').on('click', function () {
                var $this = $(this),
                    plus = $this.hasClass('ico_expand');
                if (plus) {
                    $this.removeClass('ico_expand').addClass('ico_contract');
                } else {
                    $this.removeClass('ico_contract').addClass('ico_expand');
                }
                return false;
            });

            // Adds error icon if there are errors in the product update form
            $('[data-behaviour="tab-nav-errors"] .tab-pane').each(function () {
                var productErrorListener = $(this).find('[class*="error"]:not(:empty)').closest('.tab-pane').attr('id');
                $('.tab-nav a[href="#' + productErrorListener + '"]').append('<i class="fas fa-info-circle float-right"></i>');
            });

            document.querySelectorAll('.tab-nav .nav-link').forEach(function (tab) {
                tab.addEventListener("click", function (event) {
                    window.location.hash = this.getAttribute("href");
                });
            });

            o.dashboard.filereader.init();
        },
        initWidgets: function (el) {
            /** Attach widgets to form input.
             *
             * This function is called once for the whole page. In that case el is window.document.
             *
             * It is also called when input elements have been dynamically added. In that case el
             * contains the newly added elements.
             *
             * If the element selector refers to elements that may be outside of newly added
             * elements, don't limit to elements within el. Then the operation will be performed
             * twice for these elements. Make sure that that is harmless.
             */
            o.dashboard.initDatePickers(el);
            o.dashboard.initMasks(el);
            o.dashboard.initWYSIWYG(el);
            o.dashboard.initSelects(el);
            o.dashboard.initProductImages(el);
        },
        initMasks: function (el) {
            $(el).find(':input').inputmask();
        },
        initSelects: function (el) {
            // Adds type/search for select fields
            var $selects = $(el).find('select').not('.no-widget-init select').not('.no-widget-init');
            $selects.filter('.form-stacked select').css('width', '100%');
            // $selects.filter('.form-inline select').css('width', '250px');
            // $selects.not('.related-widget-wrapper select').select2({width: 'resolve'});
            // $selects.not('.related-widget-wrapper select').select2();
            $selects.not('.related-widget-wrapper select').select2({ width: '100%' });
            $selects.filter('.related-widget-wrapper.single select').select2({
                // Keep updated labels after editing related obj
                templateResult: function (data) {
                    return $(data.element).text();
                },
                templateSelection: function (data) {
                    return $(data.element).text();
                },
                // width: 'resolve'
            });
            // $selects.filter('.related-widget-wrapper.multiple select').select2({
            //     width: '95%'
            // });
            $(el).find('select.select2').each(function (i, e) {
                var opts = {};
                if ($(e).data('ajax-url')) {
                    opts = {
                        ajax: {
                            url: $(e).data('ajax-url'),
                            dataType: 'json',
                            data: function (params) {
                                return {
                                    q: params.term,
                                    product_id: $(this).data('product-id'),
                                    class_id: $(this).data('class-id'),
                                    page: params.page || 1
                                };
                            }
                        },
                        multiple: $(e).data('multiple')
                    };
                }
                $(e).select2(opts);
            });
        },
        initDatePickers: function (el) {
            if ($.fn.datetimepicker) {

                // Set "Tempus Dominus Bootstrap 4" datetime picker's global options.
                $.fn.datetimepicker.Constructor.Default = $.extend(
                    {}, $.fn.datetimepicker.Constructor.Default, o.dashboard.options.datetimePickerConfig
                );

                var defaultDatepickerConfig = {
                    'format': o.dashboard.options.dateFormat,
                };
                var $dates = $(el).find('[data-oscarWidget="date"]').not('.no-widget-init').not('.no-widget-init *');
                $dates.each(function (ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultDatepickerConfig, {
                            'format': $ele.data('dateformat')
                        });
                    $ele.datetimepicker(config);
                });

                var defaultDatetimepickerConfig = {
                    'format': o.dashboard.options.datetimeFormat,
                    'stepping': o.dashboard.options.stepMinute
                };
                var $datetimes = $(el).find('[data-oscarWidget="datetime"]').not('.no-widget-init').not('.no-widget-init *');
                $datetimes.each(function (ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultDatetimepickerConfig, {
                            'format': $ele.data('datetimeformat'),
                            'stepping': $ele.data('stepminute')
                        });
                    $ele.datetimepicker(config);
                });

                var defaultTimepickerConfig = {
                    'format': o.dashboard.options.timeFormat,
                    'stepping': o.dashboard.options.stepMinute
                };
                var $times = $(el).find('[data-oscarWidget="time"]').not('.no-widget-init').not('.no-widget-init *');
                $times.each(function (ind, ele) {
                    var $ele = $(ele),
                        config = $.extend({}, defaultTimepickerConfig, {
                            'format': $ele.data('timeformat'),
                            'stepping': $ele.data('stepminute'),
                            'viewMode': 'times'
                        });
                    $ele.datetimepicker(config);
                });
            }
        },
        initWYSIWYG: function (el) {
            // Use TinyMCE by default
            var $textareas = $(el).find('textarea').not('.no-widget-init textarea').not('.no-widget-init');
            $textareas.filter('form.wysiwyg textarea').tinymce(o.dashboard.options.tinyConfig);
            $textareas.filter('.wysiwyg').tinymce(o.dashboard.options.tinyConfig);
        },
        initForms: function () {
            // Disable buttons when they are clicked and show a "loading" message taken from the
            // data-loading-text attribute.
            // Do not disable if button is inside a form with invalid fields.
            // This uses a delegated event so that it keeps working for forms that are reloaded
            // via AJAX: https://api.jquery.com/on/#direct-and-delegated-events
            $(document.body).on('click', '[data-loading-text]', function () {
                var $btn_or_input = $(this),
                    form = $btn_or_input.parents("form");
                if (!form || $(":invalid", form).length == 0) {
                    var d = 'disabled',
                        val = $btn_or_input.is('input') ? 'val' : 'html';
                    // push to event loop so as not to delay form submission
                    setTimeout(function () {
                        $btn_or_input[val]($btn_or_input.data('loading-text'));
                        $btn_or_input.addClass(d).attr(d, d).prop(d, true);
                    });
                }
            });
            // Display tabs that have invalid input fields
            $('input').on('invalid', function () {
                var id = $(this).closest('.tab-pane').attr('id');
                if (id) {
                    $('.bs-docs-sidenav a[href="#' + id + '"]').tab('show');
                }
            });
        },
        initProductImages: function () {
            // convert last 'extra' form into a multi-upload
            // (assumes `extra=1` in django formset)
            var $productImages = $('#product_images');
            var $extraImg = $productImages.find('.upload-image tr').last();
            o.dashboard._extraProductImg = $extraImg.clone();
            $productImages.find('span:disabled').parents('.sortable-handle').sortable('disable');

            $('tbody.upload-image').sortable({
                vertical: true,
                // forcePlaceholderSize: true,
                axis: 'y',
                itemSelector: "tr",
                group: 'serialization',
                handle: '.btn-handle',
                placeholder: 'tr-placeholder',
                cancel: '.sortable-disabled',
                onDrop: function ($item, container, _super) {
                    var $sortFields = $("input[name$=-display_order]");
                    $sortFields.each(function (i) {
                        $(this).val(i);
                    });
                    _super($item, container);
                },
            });
        },
        offers: {
            init: function () {
                dashboard.offers.adjustBenefitForm();
                $('#id_type').change(function () {
                    dashboard.offers.adjustBenefitForm();
                });
            },
            adjustBenefitForm: function () {
                var type = $('#id_type').val(),
                    $valueContainer = $('#id_value').parents('.form-group');
                if (type == 'Multibuy') {
                    $('#id_value').val('');
                    $valueContainer.hide();
                } else {
                    $valueContainer.show();
                }
            }
        },
        product_attributes: {
            init: function () {
                var type_selects = $("select[name$=type]");

                type_selects.each(function () {
                    o.dashboard.product_attributes.toggleOptionGroup($(this));
                });

                type_selects.change(function () {
                    o.dashboard.product_attributes.toggleOptionGroup($(this));
                });
            },

            toggleOptionGroup: function (type_select) {
                var option_group_select = $('#' + type_select.attr('id').replace('type', 'option_group'));
                var v = type_select.val();
                var showOptionGroup = v === 'option' || v === 'multi_option';
                option_group_select.parent().parent().toggle(showOptionGroup);
                if (showOptionGroup) {
                    option_group_select.attr('required', 'required');
                } else {
                    option_group_select.attr('required', null);
                }
            }
        },
        ranges: {
            init: function () {
                $('[data-behaviours~="remove"]').click(function () {
                    var $this = $(this);
                    $this.parents('table').find('input').prop('checked', false);
                    $this.parents('tr').find('input').prop('checked', true);
                    $this.parents('form').submit();
                });
            }
        },
        product: {
            initProductClass: function () {
                const selectElement = document.getElementById('id_product_class');
                $(selectElement).on("select2:select", function () {
                    const form = selectElement.closest('form');
                    form.submit();
                });
            }
        },
        orders: {
            initTable: function () {
                var table = $('form table'),
                    lines = document.querySelectorAll('[data-id="line-container"]'),
                    checkboxes = document.querySelectorAll('.table input[type="checkbox"]'),
                    actionsLinesDiv = document.getElementById('actions_lines'),
                    input = $('<input type="checkbox"/>');
                $('th:first', table).prepend(input);
                function toggleActionsDiv() {
                    if (actionsLinesDiv) {
                        const isChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
                        if (isChecked) {
                            actionsLinesDiv.classList.remove('d-none');
                        } else {
                            actionsLinesDiv.classList.add('d-none');
                        }
                    }
                };
                $(input).change(function () {
                    $('tr', table).each(function () {
                        $('td:first input', this).prop("checked", $(input).is(':checked'));
                    });
                    toggleActionsDiv();
                });
                checkboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', function () {
                        toggleActionsDiv();
                    });
                });

                if (lines) {
                    $(lines).each(function () {
                        var input_container = $(this).find('[data-id="line-input"]');
                        var input_checkbox = $(this).find('input[type="checkbox"]');
                        var input_field = $(input_container).find('input');
                        var more = $(this).find('[data-id="order-button-plus"]');
                        var less = $(this).find('[data-id="order-button-minus"]');
                        more.on('click', function () {
                            if ($(input_field).val() < $(input_field).attr('max')) {
                                $(input_field).val(parseInt($(input_field).val()) + 1);
                                $(less).prop('disabled', false);
                            }
                            if ($(input_field).val() == $(input_field).attr('max')) {
                                $(this).prop('disabled', true);
                            }
                            $(input_checkbox).prop("checked", true);
                            toggleActionsDiv();
                        });
                        less.on('click', function () {
                            if ($(input_field).val() > 0) {
                                $(input_field).val(parseInt($(input_field).val()) - 1);
                                $(more).prop('disabled', false);
                            }
                            if ($(input_field).val() == 0) {
                                $(this).prop('disabled', true);
                            }
                            $(input_checkbox).prop("checked", true);
                            toggleActionsDiv();
                        });
                    })
                }

                toggleActionsDiv();

                var storeForm = document.getElementById('store_form');
                if (storeForm) {
                    var selectInput = storeForm.querySelector('select');
                    selectInput.addEventListener('change', function () {
                        storeForm.submit();
                    });
                }

            }
        },
        evotor: {
            initTable: function () {
                var forms = $('form')
                forms.each(function () {
                    var table = $(this).find('table');
                    if ($(table).length > 0) {
                        var checkboxes = $(this).find('input[type="checkbox"]');
                        var actionsLinesDiv = $(this).find('[data-id="actions-lines"]');
                        var input = $('<input type="checkbox"/>');
                        $(input).change(function () {
                            $('tr', table).each(function () {
                                $('td:first input', this).prop("checked", $(input).is(':checked'));
                            });
                            toggleActionsDiv();
                        });
                        $('th:first', table).prepend(input);
                        function toggleActionsDiv() {
                            if ($(actionsLinesDiv).length > 0) {
                                const isChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);
                                if (isChecked) {
                                    actionsLinesDiv.removeClass('d-none');
                                } else {
                                    actionsLinesDiv.addClass('d-none');
                                }
                            }
                        };
                        checkboxes.each(function () {
                            var checkbox = $(this);
                            checkbox.change(function () {
                                var inputContainer = checkbox.closest('td').find('[data-id="selected-line-input"]');
                                if (inputContainer.length) {
                                    if (checkbox.is(':checked')) {
                                        inputContainer.removeClass('d-none');
                                        var input_field = inputContainer.find('input');
                                        input_field.val(input_field.attr('max'));
                                        inputContainer.find('[data-id="order-button-plus"]').prop('disabled', true);
                                        inputContainer.find('[data-id="order-button-minus"]').prop('disabled', false);
                                        checkbox.addClass('d-none');
                                    } else {
                                        inputContainer.addClass('d-none');
                                        checkbox.removeClass('d-none');
                                    }
                                }
                                toggleActionsDiv();
                            });
                        });
                        var lines_input = $('[data-id="selected-line-container"]');
                        if ($(lines_input).length > 0) {
                            $(lines_input).each(function () {
                                var input_container = $(this).find('[data-id="selected-line-input"]');
                                var input_checkbox = $(this).find('input[type="checkbox"]');
                                var input_field = $(input_container).find('input');
                                var more = $(this).find('[data-id="order-button-plus"]');
                                var less = $(this).find('[data-id="order-button-minus"]');
                                more.on('click', function () {
                                    if ($(input_field).val() < $(input_field).attr('max')) {
                                        $(input_field).val(parseInt($(input_field).val()) + 1);
                                        $(less).prop('disabled', false);
                                    }
                                    if ($(input_field).val() == $(input_field).attr('max')) {
                                        $(this).prop('disabled', true);
                                    }
                                });

                                less.on('click', function () {
                                    if ($(input_field).val() > 0) {
                                        $(input_field).val(parseInt($(input_field).val()) - 1);
                                        $(more).prop('disabled', false);
                                    }
                                    if ($(input_field).val() == 0) {
                                        $(this).prop('disabled', true);
                                        $(input_container).addClass('d-none');
                                        $(input_checkbox).removeClass('d-none');
                                        $(input_checkbox).prop("checked", false);
                                    }
                                });
                            })
                        }
                        toggleActionsDiv();
                    }
                });

                var storeForm = document.getElementById('store_form');
                if (storeForm) {
                    var selectInput = storeForm.querySelector('select');
                    selectInput.addEventListener('change', function () {
                        storeForm.submit();
                    });
                }
            }
        },
        reordering: (function () {
            var options = {
                handle: '.btn-handle',
                submit_url: '#'
            },
                saveOrder = function (data) {
                    // Get the csrf token, otherwise django will not accept the
                    // POST request.
                    var csrf = o.getCsrfToken();
                    $.ajax({
                        type: 'POST',
                        data: $.param(data),
                        dataType: "json",
                        url: options.submit_url,
                        beforeSend: function (xhr) {
                            xhr.setRequestHeader("X-CSRFToken", csrf);
                        }
                    });
                },
                init = function (user_options) {
                    options = $.extend(options, user_options);
                    var group = $(options.wrapper).sortable({
                        vertical: true,
                        axis: 'y',
                        group: 'serialization',
                        containerSelector: 'tbody',
                        itemSelector: 'tr',
                        handle: options.handle,
                        cancel: '.sortable-disabled',
                        onDrop: function ($item, container, _super) {
                            var data = group.sortable("serialize");
                            saveOrder(data);
                            _super($item, container);
                        },
                        placeholder: 'tr-placeholder',
                        serialize: function (parent, children, isContainer) {
                            if (isContainer) {
                                return children;
                            }
                            else {
                                var parts = parent.attr('id').split('_');
                                return { 'name': parts[0], 'value': parts[1] };
                            }
                        },
                    });
                };

            return {
                init: init,
                saveOrder: saveOrder
            };
        }()),
        filereader: {
            init: function () {
                // Add local file loader to update image files on change in
                // dashboard. This will provide a preview to the selected
                // image without uploading it. Upload only occures when
                // submitting the form.
                if (window.FileReader) {
                    $('input[type="file"]').change(onFileChange);
                }
            },
        },
        thumbnails: {
            init: function () {
                var imageModal = $("#product-image-modal"),
                    thumbnails = $('.sub-image');
                thumbnails.click(function (e) {
                    e.preventDefault();
                    var a = $(this);
                    imageModal.find('h4').text(a.find('img').attr('alt'));
                    imageModal.find('img').attr('src', a.data('original'));
                    imageModal.modal();
                });
            }
        },
    };

    return o;

})(dashboard || {}, jQuery);
