let currentPage = 1
let totalPages = 1;
let nextPageUrl = null;
let prevPageUrl = null;;

const restaurantsGrid = document.getElementById('restaurants-grid');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');


const searchDropdown = document.getElementById('search-dropdown');
const locationForm = document.getElementById('location-form');
const imageForm = document.getElementById('image-form');
const locationSearchBtn = document.getElementById('location-search-btn');

function fetchRestaurants(url = null) {
  if(url === null) {
    url = "http://127.0.0.1:8000/api/restaurants/?page=1&page_size=12"
  }

  fetch(url)
    .then(response => response.json())
    .then(data => {
      totalPages = data.total_pages;
      currentPage = data.current_page;
      nextPageUrl = data.next_page;
      prevPageUrl = data.previous_page;

      updatePaginationButtons();
      renderRestaurants(data.restaurants);
    })
    .catch(error => {
      console.error("Error fetching data:", error);
    })
}

function renderRestaurants(restaurants) {
  // Clear previous restaurant data
  restaurantsGrid.innerHTML = '';

  // Render each restaurant as a card
  restaurants.forEach(restaurant => {
    const restaurantCard = document.createElement('div');
    restaurantCard.classList.add('restaurant-card');

    const cuisinesArray = restaurant.cuisines;
    //console.log(restaurant.cuisines)
    const ratingClass =
    restaurant.aggregate_rating >= 4
      ? 'rating-green'
      : restaurant.aggregate_rating > 3
      ? 'rating-yellow'
      : 'rating-red';
    const imageUrl = restaurant.image_url 
      ? restaurant.image_url 
      : "./images/default_restaurant.png";
    const cuisinesHTML = cuisinesArray.map(cuisine => `<button class="cuisine-btn">${cuisine}</button>`).join('');
    restaurantCard.innerHTML = `
      <a href = "restaurant_detail.html?id=${restaurant.restaurant_id}" class = "restaurant-link">
        <img src="${imageUrl}" alt="${restaurant.name}" />
        <h4>${restaurant.name}</h4>
        <div class = "cuisine-rating-container">
          <div class="cuisines">${cuisinesHTML}</div>
          <button class="rating-btn ${ratingClass}">${restaurant.aggregate_rating} ★</button>
        </div>
      </a>
    `;

    restaurantsGrid.appendChild(restaurantCard);
  });
}

function updatePaginationButtons() {
  // Enable or disable the previous button
  prevBtn.disabled = !prevPageUrl;
  
  // Enable or disable the next button
  nextBtn.disabled = !nextPageUrl;
}

// Initially fetch the first page


// Handle previous and next page clicks
prevBtn.addEventListener('click', () => {
  if (prevPageUrl) {
    fetchRestaurants(prevPageUrl); // Fetch data for the previous page
  }
});

nextBtn.addEventListener('click', () => {
  if (nextPageUrl) {
    fetchRestaurants(nextPageUrl); // Fetch data for the next page
  }
});



// Update form visibility based on dropdown selection
searchDropdown.addEventListener('change', (event) => {
  if (event.target.value === 'location') {
    locationForm.style.display = 'flex';
    imageForm.style.display = 'none';
  } else if (event.target.value === 'image') {
    locationForm.style.display = 'none';
    imageForm.style.display = 'flex';
  }
});


// Handle search by location
locationSearchBtn.addEventListener('click', () => {
  const latitude = document.getElementById('latitude').value;
  const longitude = document.getElementById('longitude').value;
  const radius = document.getElementById('radius').value;
  //console.log(radius)
  if (latitude && longitude && radius) {
    const url = `http://127.0.0.1:8000/api/search-restaurants/?latitude=${latitude}&longitude=${longitude}&radius=${radius}`;
    console.log('Fetching restaurants by location:', url);

    fetchRestaurants(url)
  } else if(latitude && longitude) {
    const url = `http://127.0.0.1:8000/api/search-restaurants/?latitude=${latitude}&longitude=${longitude}`;
    console.log('Fetching restaurants by location:', url);

    fetchRestaurants(url)
  }
  else {
    alert('Please enter valid latitude and longitude!');
  }
});



fetchRestaurants();