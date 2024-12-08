const params = new URLSearchParams(window.location.search);
const restaurantId = params.get('id');

// Get the container for restaurant details
const restaurantDetailContainer = document.getElementById('restaurant-detail');

function fetchRestaurant(restaurantId) {
  const url = `http://127.0.0.1:8000/api/restaurant/${restaurantId}/`;

  fetch(url)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      
      const cuisinesArray = data.cuisines;
      const cuisinesHTML = cuisinesArray.map(cuisine => `<button class="cuisine-btn">${cuisine}</button>`).join('');
      const hasTableBookClass = data.has_table_booking == true ? 'rating-green' : 'rating-red';
      const avgCostForTwoClass = data.avg_cost_for_two == true ? 'rating-green' : 'rating-red';
      const isDeliveringClass = data.is_delivering == true ? 'rating-green' : 'rating-red';
      const imageUrl = data.image_url 
      ? data.image_url
      : "./images/default_restaurant.png";
      restaurantDetailContainer.innerHTML = `
        <img src = "${imageUrl}" alt = "${data.name}">
        <div class = "restaurant-detail-name">
          <h1>${data.name}</h1>
          <h5> ${data.address}</h5>
          <h5>${data.locality}</h5>
        </div>
        <div class = "restaurant-detail-rating">
          <button class = "rating-btn" style = "background-color : #${data.rating_color}"> ${data.aggregate_rating}</button>
          <p> (${data.rating_text})</p>
        </div>
        <h3>Average cost for two :  ${data.avg_cost_for_two} </h3>
        <h3>Votes :  ${data.votes} </h3>
        <div class = "restaurant-detail-cuisines">
          <h3>Cusines: </h3>
          <div class="cuisines">${cuisinesHTML}</div>
        </div>
        <div class = "restaurant-detail-btns">
          <button class="${hasTableBookClass}">Has Table Booking</button>
          <button class="${isDeliveringClass}">Is Delivering</button>
        </div>
        
      `;
    })
    .catch(error => {
      console.error("Error fetching restaurant details:", error);
      restaurantDetailContainer.innerHTML = `<p>Error fetching restaurant details. Please try again later.</p>`;
    });
}

fetchRestaurant(restaurantId);