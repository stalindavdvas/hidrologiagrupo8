let index = 0;
const images = document.getElementById('carousel-images');
const total = images.children.length;

function showSlide(i) {
  index = (i + total) % total;
  images.style.transform = `translateX(-${index * 100}%)`;
}

function nextSlide() {
  showSlide(index + 1);
}

function prevSlide() {
  showSlide(index - 1);
}

setInterval(nextSlide, 5000);
