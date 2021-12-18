const artistInp = document.getElementById('artist_id');
const venueInp = document.getElementById('venue_id');
const starttimeImp = document.getElementById('start_time');
document.getElementById('form').onsubmit = function (e) {
    e.preventDefault();
    const artist = artistInp.value;
    const venue = venueInp.value;
    const starttime = starttimeImp.value;
    artistInp.value = '';
    venueInp.value = '';
    fetch('/shows/create', {
        method: 'POST',
        body: JSON.stringify({
            'artist_id': artist,
            'venue_id': venue,
            'start_time': starttime
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(jsonResponse => {
            console.log('response', jsonResponse);
        })
    }
