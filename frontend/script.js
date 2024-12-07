let currentPage = 1
let totalPages = 1;
let nextPageUrl = null;
let prevPageUrl = null;;

const restaurantsGrid = document.getElementById('restaurants-grid');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');


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
    restaurant.aggregate_rating > 4
      ? 'rating-green'
      : restaurant.aggregate_rating > 3
      ? 'rating-yellow'
      : 'rating-red';
    const imageUrl = restaurant.image_url 
      ? restaurant.image_url 
      : "./images/default_restaurant.png";
    const cuisinesHTML = cuisinesArray.map(cuisine => `<button class="cuisine-btn">${cuisine}</button>`).join('');
    restaurantCard.innerHTML = `
      <img src="${imageUrl}" alt="${restaurant.name}" />
      <h4>${restaurant.name}</h4>
      <div class = "cuisine-rating-container">
        <div class="cuisines">${cuisinesHTML}</div>
        <button class="rating-btn ${ratingClass}">${restaurant.aggregate_rating} ★</button>
      </div>
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

fetchRestaurants();