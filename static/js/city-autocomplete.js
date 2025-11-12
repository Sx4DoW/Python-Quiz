document.addEventListener('DOMContentLoaded', function() {
    let timer;
    let validCities = [];
    const cityInput = document.getElementById('city');
    const form = cityInput.closest('form');
    
    cityInput.addEventListener('input', function(e) {
        clearTimeout(timer);
        const query = e.target.value;
        if (query.length < 2) {
            validCities = [];
            return;
        }
        
        timer = setTimeout(() => {
            fetch('/api/search-cities?q=' + encodeURIComponent(query))
                .then(r => r.json())
                .then(data => {
                    const datalist = document.getElementById('city-suggestions');
                    datalist.innerHTML = '';
                    validCities = data.cities.map(c => c.name);
                    data.cities.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city.name;
                        option.textContent = city.display;
                        datalist.appendChild(option);
                    });
                });
        }, 300);
    });
    
    // Validate on form submit that city is from the list
    form.addEventListener('submit', function(e) {
        const cityValue = cityInput.value.trim();
        if (!validCities.includes(cityValue)) {
            e.preventDefault();
            alert('Please select a city from the suggestions list');
            cityInput.focus();
        }
    });
});
