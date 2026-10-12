      let tooday_graf = {
            "location": {
                "city": "-",
                "country": "-",
                "date": "2026-10-11"
            },
            "condition": {
                "alt": "-",
                "icon": "-",
                "type": "-"
            },
            "hourly_condition": [
                {
                    "alt": "-",
                    "icon": "-",
                    "type": "-"
                },
                {
                    "alt": "-",
                    "icon": "-",
                    "type": "-"
                }
            ],
            "wind_force": "-",
            "temperature": 0,
            "feels_like_temp": 0,
            "water_temperature": 0,
            "humidity": 0,
            "pressure": 0,
            "uv_index": 0
        }

        let week_graf = {
            "location": {
                "city": "Moscow",
                "country": "Russia",
                "date": "2026-10-07"
            },
            "weather_for_week": [

            ]
        }

        const SHORT_WEEKDAYS = {
            "понедельник": "Пн",
            "вторник": "Вт",
            "среда": "Ср",
            "четверг": "Чт",
            "пятница": "Пт",
            "суббота": "Сб",
            "воскресенье": "Вс"
        }

        async function getDataTooday() {
            const response = await fetch("./tooday.json");
            if (!response.ok) {
                throw new Error("Error in response_tooday.ok");
            }

            return await response.json();
        }
        async function main_tooday() {
            const data = await getDataTooday();
            tooday_graf = data;
        }

        async function getDataWeek() {
            const response = await fetch("./week.json");
            if (!response.ok) {
                throw new Error("Error in response_week.ok");
            }

            return await response.json();
        }

        async function main_week() {
            const data_week = await getDataWeek();
            week_graf = data_week;
        }

        function formatDateRu(isoDate) {
            const [year, month, day] = isoDate.split('-').map(Number);
            const date = new Date(year, month - 1, day);

            return new Intl.DateTimeFormat('ru-RU', {
                day: 'numeric',
                month: 'long',
                year: 'numeric'
            }).format(date).replace(/\s*г\.$/, '');
        }

        function getValue(obj, key, fallback = null) {
            if (key == null) return fallback;
            return obj[key] ?? fallback;
        }

        function capitalize(str) {
            return str.charAt(0).toUpperCase() + str.slice(1);
        }


        function formatDateRuWeek(isoDate) {
            const [year, month, day] = isoDate.split('-').map(Number);
            const date = new Date(year, month - 1, day);

            const weekDayFull = new Intl.DateTimeFormat('ru-RU', {
                weekday: 'long'
            }).format(date).toLowerCase();

            const parts = new Intl.DateTimeFormat('ru-RU', {
                day: 'numeric',
                month: 'long',
            }).format(date);

            const weekOrDay = getValue(SHORT_WEEKDAYS, weekDayFull, weekDayFull);
            return `${weekOrDay} ${parts}`;
        }



        main_tooday().then(() => {
            //дневной график погоды
            document.getElementById("city").textContent = tooday_graf.location.city;
            document.getElementById("temp-value").textContent = "+" + tooday_graf.temperature;
            document.getElementById("main_date").textContent = formatDateRu(tooday_graf.location.date);
            document.getElementById("humidity").textContent = `${tooday_graf.humidity} %`;
            document.getElementById("pressure").textContent = `${tooday_graf.pressure} мм рт. ст.`;
            document.getElementById("uv_index").textContent = `${tooday_graf.uv_index}`;
            document.getElementById("current_weather").textContent = `${tooday_graf.condition.alt}`;
            document.getElementById("img_tooday").src = `img/${tooday_graf.condition.icon}`;
            document.getElementById("img_tooday").alt = `${tooday_graf.condition.alt}`;
            document.getElementById("wind_force").textContent = `${tooday_graf.wind_force}`;
            document.getElementById("water_temperature").textContent = tooday_graf.water_temperature>0?`+${tooday_graf.water_temperature}`:`-${tooday_graf.water_temperature}`;
            document.getElementById("feels_like_temp").textContent = tooday_graf.feels_like_temp>0?`Ощущается как +${tooday_graf.feels_like_temp}`:`Ощущается как -${tooday_graf.feels_like_temp}`;

            //проход по блокам с временем и img циклом:
            const forecast_tooday = tooday_graf.hourly_condition;
            const items = document.querySelectorAll('.hourly-item');
            items.forEach((item)=>{
                const idx = Number(item.dataset.todayIndex);
                const time_day = forecast_tooday[idx];

                if(!time_day){
                    item.style.display = 'none';
                    return;
                }

                item.querySelectorAll('[data-field-tooday]').forEach((el)=>{
                    const field_tooday = el.dataset.fieldTooday
                    const value = time_day[field_tooday];

                    if (el.tagName === "IMG") {
                        el.src = `img/${value}`;
                        el.alt = time_day.alt ?? '';
                    }
                })
            })

        }).catch((error) => {
            console.error("Error", error);

        });


        main_week().then(() => {
            //недельный график погоды
            const forecast = week_graf.weather_for_week;
            const items = document.querySelectorAll(".day-item");

            items.forEach((item) => {
                //берем индекс блока из html и ищем блок из json с таким-же индексом 
                const idx = Number(item.dataset.dayIndex);
                const day = forecast[idx];


                //проверка на существование дня в прогнозе
                if (!day) {
                    item.style.display = 'none';
                    return;
                }

                //обход всех data-field блоков и подставление данных по их значениям
                item.querySelectorAll('[data-field]').forEach((el) => {
                    const field = el.dataset.field;
                    const value = day[field];

                    //логика распределения значений
                    if (el.tagName === "IMG") {
                        el.src = `img/${value}`;
                        el.alt = day.alt ?? '';
                    } else if (field === "date") {
                        el.textContent = formatDateRuWeek(value);
                    } else if (field === "temp") {
                        el.textContent = "+" + value;
                    } else {
                        el.textContent = value;
                    }
                })
            })

        }).catch((error) => {
            console.error("Error", error);
        });