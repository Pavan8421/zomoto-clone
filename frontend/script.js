let currentPage = 1
let totalPages = 1;
let nextPageUrl = null;
let prevPageUrl = null;;

const restaurantsGrid = document.getElementById('restaurants-grid');
const prevBtn = document.getElementById('prev-btn');
const nextBtn = document.getElementById('next-btn');


const searchBtn = document.getElementById('search-btn');

let latitude = '';
let longitude = '';
let radius = '';
let cuisine_name = '';

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

      // Update the URL using history.pushState to reflect the current state
      const queryParams = new URLSearchParams();
      if (latitude) queryParams.append('latitude', latitude);
      if (longitude) queryParams.append('longitude', longitude);
      if (radius) queryParams.append('radius', radius);
      if(cuisine_name) queryParams.append('cuisine', cuisine_name);
      queryParams.append('page', currentPage);
      history.pushState(null, '', '?' + queryParams.toString());
      console.log(history);
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



// Event listener for submit button
searchBtn.addEventListener('click', async () => {
  latitude = document.getElementById('latitude').value;
  longitude = document.getElementById('longitude').value;
  radius = document.getElementById('radius').value;

  const imageInput = document.getElementById("image-upload");

  // If image is selected, send a POST request
  if (imageInput.files.length > 0) {
    const formData = new FormData();
    formData.append('image', imageInput.files[0]);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/search-restaurants-by-image/", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      console.log("Response Data:", data);
      // totalPages = data.total_pages;
      // currentPage = data.current_page;
      // nextPageUrl = data.next_page;
      // prevPageUrl = data.previous_page;
      // updatePaginationButtons();
      // renderRestaurants(data.restaurants);

      cuisine_name = data.cuisine

      const query = new URLSearchParams();
      if (latitude) query.append("latitude", latitude);
      if (longitude) query.append("longitude", longitude);
      if (radius) query.append("radius", radius);
      if(cuisine_name) query.append("cuisine", cuisine_name);
      const url = `http://127.0.0.1:8000/api/restaurants/?${query.toString()}`;
      fetchRestaurants(url);

      // // Update the URL using history.pushState to reflect the current state
      // const queryParams = new URLSearchParams();
      // if (latitude) queryParams.append('latitude', latitude);
      // if (longitude) queryParams.append('longitude', longitude);
      // if (radius) queryParams.append('radius', radius);
      // queryParams.append('page', currentPage);
      // console.log(queryParams.toString())
      // history.pushState(null, '', '?' + queryParams.toString());

    } catch (error) {
      console.error("Error fetching data:", error);
    }

  } else if (latitude || longitude || radius) {
    // If no image is selected, send a GET request with the parameters
    const query = new URLSearchParams();
    if (latitude) query.append("latitude", latitude);
    if (longitude) query.append("longitude", longitude);
    if (radius) query.append("radius", radius);

    const url = `http://127.0.0.1:8000/api/restaurants/?${query.toString()}`;
    fetchRestaurants(url);
  }
});

window.addEventListener('load', () => {
  const queryParams = new URLSearchParams(window.location.search);
  console.log(queryParams)
  latitude = queryParams.get('latitude');
  longitude = queryParams.get('longitude');
  radius = queryParams.get('radius');
  cuisine_name = queryParams.get('cuisine');
  const page = queryParams.get('page') || 1;

  let url = "http://127.0.0.1:8000/api/restaurants/?page=" + page;

  // If parameters are available, append them to the URL
  if (latitude) {
    url += `&latitude=${latitude}`;
  }

  if (longitude) {
    url += `&longitude=${longitude}`;
  }

  if (radius) {
    url += `&radius=${radius}`;
  }

  if(cuisine_name) {
    url += `&cuisine=${cuisine_name}`;
  }
  console.log(url)
  // Fetch restaurants based on the constructed URL
  fetchRestaurants(url);
});
