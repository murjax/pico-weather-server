console.log('app loaded');

const host = '192.168.0.132';
const socket = new WebSocket(`ws://${host}/info`);

socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  document.getElementById('temperature').innerHTML = `Temperature is ${data.temperature}`;
  document.getElementById('humidity').innerHTML = `Humidity is ${data.humidity}`;
}
