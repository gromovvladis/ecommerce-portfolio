let datapicker;
const localLang = {
    days: ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'],
    daysShort: ['Вос', 'Пон', 'Вто', 'Сре', 'Чет', 'Пят', 'Суб'],
    daysMin: ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'],
    months: ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'],
    monthsShort: ['Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября', 'Ноября', 'Декабря'],
    today: 'Сегодня',
    clear: 'Очистить',
    dateFormat: 'dd.MM.yyyy',
    timeFormat: 'HH:mm',
    firstDay: 1
};

let minHours = 10;
let maxHours = 22;
let maxMinutes = 60;
let minMinutes = 0;

const today = new Date();
let hoursMore = today.getUTCMinutes() > 20 ? 3 : 2;

let minDate = new Date(today.getFullYear(), today.getMonth(), today.getDate(), today.getHours() + hoursMore, 0, 0);
let maxDate = new Date();
maxDate.setUTCDate(minDate.getUTCDate() + 14);
let selectedDate = new Date(minDate);
let selectedTime = minDate.getTime();

datapicker = new AirDatepicker('#delivery_time_later', {
    autoClose: false,
    isMobile: true,
    timepicker: true,
    altField: "#id_order_time",
    // altFieldDateFormat: "dd.MM.yyyy HH:mm",
    dateFormat: 'd MMM',
    timeFormat: 'HH:mm',
    minutesStep: 15,
    toggleSelected: false,
    locale: localLang,
    dateTimeSeparator: " ",
    minHours: minHours,
    maxHours: maxHours,
    maxMinutes: maxMinutes,
    minMinutes: minMinutes,
    selectedDates: selectedDate,
    selectedTime: selectedTime,
    minDate: minDate,
    maxDate: maxDate,
    // onShow(isFinished) {
    //     if (!isFinished) {
    //         AirDatepickerTime(updateSelected=false);
    //     }
    // },
    altFieldDateFormat(date) {
        return new Date(date).toISOString();
    },
});

function AirDatepickerTime() {
    fetch(url_delivery_later, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token,
        }
    })
    .then(response => response.json())
    .then(data => {
        const { minDate: minDateRaw, maxDate: maxDateRaw, minHours, maxHours } = data.datapicker;
        minDate = new Date(minDateRaw);
        maxDate = new Date(maxDateRaw);
        selectedDate = new Date(minDate);
        selectedTime = minDate.getTime();
        datapicker.update({
            minHours: minHours,
            maxHours: maxHours,
            selectedDates: selectedDate,
            selectedTime: selectedTime,
            minDate: minDate,
            maxDate: maxDate,
        });
        
    })
    .catch(error => console.error('Error:', error));
}

AirDatepickerTime();
