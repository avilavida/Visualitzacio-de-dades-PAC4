document.addEventListener('DOMContentLoaded', () => {
  const baseLayers = [
    { id: 'decoration', src: 'img/1980/genre_map_decoration.png', alt: 'Decoration' },
    { id: 'data', src: 'img/1980/genre_map_data.png', alt: 'Data' },
    { id: 'elements', src: 'img/common/elements.png', alt: 'Elements' }
  ];

  const genreLayers = {
    Classical: 'Classical.png',
    Electronic: 'Electronic.png',
    Folk_Country: 'Folk_Country.png',
    Indie_Asian_Jazz: 'Indie_Asian_Jazz.png',
    Metal: 'Metal.png',
    Pop_Rock: 'Pop_Rock.png',
    Urban_Latin: 'Urban_Latin.png'
  };

  let genreData = {};
  fetch('data/genres_summary.json')
  .then(response => response.json())
  .then(data => {
    genreData = data;
  });

  const genreColors = {
    '33,120,181': 'Classical',
    '51,162,50': 'Folk & Country',
    '214,41,42': 'Indie / Asian / Jazz',
    '233,151,208': 'Urban & Latin',
    '250,134,32': 'Electronic',
    '152,104,94': 'Pop & Rock',
    '151,106,190': 'Metal'
  };

  const decades = ['1980', '1990', '2000', '2010', '2020'];

  const animationSteps = [];
  decades.forEach((decade, index) => {
    animationSteps.push(decade); // ex: '1980'
    if (index < decades.length - 1) {
      for (let i = 1; i <= 5; i++) {
        animationSteps.push(`${decade}/interpolated_${i}`);
      }
    }
  });

  const container = document.getElementById('container');
  const layerSelector = document.getElementById('layerSelector');
  const toggleElements = document.getElementById('toggleElements');
  const opacitySlider = document.getElementById('opacitySlider');
  const opacityElement = document.getElementById('opacityControlGroup')
  const playButton = document.getElementById('playButton');
  const prevButton = document.getElementById('prevButton');
  const nextButton = document.getElementById('nextButton');

  let currentGenreImg = null;
  let selectedGenre = null;
  let isPlaying = false;
  let currentStepIndex = 0;
  let currentDecade = decades[0]

  // Helper: crea una imatge dins el contenidor
  function createImage(id, src, alt) {
    const img = document.createElement('img');
    img.id = id;
    img.src = src;
    img.alt = alt;
    img.classList.add('genre-layer');
    container.appendChild(img);
    return img;
  }

  // Carreguem les capes base
  baseLayers.forEach(layer => {
    createImage(layer.id, layer.src, layer.alt);
  });

  function loadDecadeLayers(folder) {
    // Determina si és una dècada (ex: '1980') o un interpolat (ex: '1980/interpolated_1')
    currentDecade = folder.split('/')[0];

    const isInterpolated = folder.includes('/');
  
    // Carreguem data
    document.getElementById('data').src = `img/${folder}/genre_map_data.png`;
  
    // Carreguem decoration només si NO és interpolació
    if (!isInterpolated) {
      document.getElementById('decoration').src = `img/${folder}/genre_map_decoration.png`;
    }
  
    // Actualitza la capa de gènere si està seleccionada
    if (currentGenreImg) {
      container.removeChild(currentGenreImg);
      currentGenreImg = null;
    }
  
    if (selectedGenre) {
      const genrePath = `img/${folder}/${selectedGenre}.png`;
      currentGenreImg = createImage('genre', genrePath, selectedGenre);
      currentGenreImg.style.opacity = 1 - (opacitySlider.value / 100);
    }
  
    // Actualitza també opacitat de la capa base
    const dataLayer = document.getElementById('data');
    if (selectedGenre && dataLayer) {
      dataLayer.style.opacity = 0.3 + 0.7 * (opacitySlider.value / 100);
    } else if (dataLayer) {
      dataLayer.style.opacity = 1;
    }
  }

  function updateBaseOpacity(sliderVal) {
    const dataLayer = document.getElementById('data');
    if (dataLayer) {
      const opacity = selectedGenre ? 0.3 + 0.7 * (sliderVal / 100) : 1;
      dataLayer.style.opacity = opacity;
    }
  }

  function updateGenreOpacity(sliderVal) {
    if (currentGenreImg) {
      currentGenreImg.style.opacity = 1 - (sliderVal / 100);
    }
  }

  function updateAllOpacities() {
    const sliderVal = opacitySlider.value;
    updateBaseOpacity(sliderVal);
    updateGenreOpacity(sliderVal);
  }

  function updateButtonsState() {
    playButton.classList.toggle('active', isPlaying);
    prevButton.disabled = isPlaying;
    nextButton.disabled = isPlaying;
  }

  // Event: selecció de gènere
  layerSelector.addEventListener('change', () => {
    const selected = layerSelector.value;
    selectedGenre = genreLayers[selected] ? selected : null;

    if (currentGenreImg) {
      container.removeChild(currentGenreImg);
      currentGenreImg = null;
    }

    if (selectedGenre) {
      const genrePath = `img/${decades[0]}/${genreLayers[selectedGenre]}`;
      currentGenreImg = createImage('genre', genrePath, selectedGenre);
      opacityElement.classList.remove('hidden');
    } else {
      opacityElement.classList.add('hidden');
    }

    updateAllOpacities();
  });

  // Event: toggle "elements"
  toggleElements.addEventListener('change', () => {
    const elementsLayer = document.getElementById('elements');
    if (!elementsLayer) return;
    elementsLayer.style.display = toggleElements.checked ? 'block' : 'none';
  });

  // Event: slider d’opacitat
  opacitySlider.addEventListener('input', () => {
    updateAllOpacities();
  });

  // Animació loop
  function stepAnimation() {
    if (!isPlaying) return;
    const folder = animationSteps[currentStepIndex];
    loadDecadeLayers(folder);
    currentStepIndex = (currentStepIndex + 1) % animationSteps.length;
    setTimeout(stepAnimation, 800); // Ajusta la durada segons preferències
  }

  // Event: Play / Pause
  playButton.addEventListener('click', () => {
    if (isPlaying) {
      isPlaying = false;
      updateButtonsState();
      return;
    }
    isPlaying = true;
    updateButtonsState();
    stepAnimation();
  });

  // Event: Anterior
  prevButton.addEventListener('click', () => {
    if (isPlaying) return;
    currentStepIndex = (currentStepIndex - 1 + animationSteps.length) % animationSteps.length;
    loadDecadeLayers(animationSteps[currentStepIndex]);
  });

  // Event: Següent
  nextButton.addEventListener('click', () => {
    if (isPlaying) return;
    currentStepIndex = (currentStepIndex + 1) % animationSteps.length;
    loadDecadeLayers(animationSteps[currentStepIndex]);
  });

  function showInfoBox(event, genre, decade) {
    if (!genreData.genres[genre]) {
      return;
    }

    const decadeKey = `${parseFloat(decade).toFixed(1)}`;
  
    const globalInfo = genreData.genres[genre];
    const decadeInfo = genreData.decades[decadeKey]?.[genre] || {};
  
    const htmlContent = `
      <strong>Genre:</strong> ${genre}<br>
      <strong>Total cançons:</strong> ${globalInfo.num_songs}<br>
      <strong>Total decade ${parseInt(decadeKey)}:</strong> ${decadeInfo.num_songs || 'N/A'}<br>
      <strong>Mean energy:</strong> ${(decadeInfo.avg_energy ?? globalInfo.avg_energy).toFixed(2)}<br>
      <strong>Mean valence:</strong> ${(decadeInfo.avg_valence ?? globalInfo.avg_valence).toFixed(2)}
    `;
  
    const box = document.getElementById('infoBox');
    box.innerHTML = htmlContent;
    box.style.left = `${event.pageX + 10}px`;
    box.style.top = `${event.pageY + 10}px`;
    box.classList.remove('hidden');
  }
  
  function hideInfoBox() {
    document.getElementById('infoBox').classList.add('hidden');
  }

  function isSimilarColor(rgb1, rgb2, tolerance = 10) {
    const [r1, g1, b1] = rgb1;
    const [r2, g2, b2] = rgb2;
    return (
      Math.abs(r1 - r2) <= tolerance &&
      Math.abs(g1 - g2) <= tolerance &&
      Math.abs(b1 - b2) <= tolerance
    );
  }

  document.getElementById('container').addEventListener('click', (event) => {
    const dataLayer = document.getElementById('data');
    if (!dataLayer) return;
  
    let canvas = document.getElementById('tempCanvas');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'tempCanvas';
      canvas.style.display = 'none';
      document.body.appendChild(canvas);
    }
  
    const ctx = canvas.getContext('2d');
    canvas.width = dataLayer.naturalWidth;
    canvas.height = dataLayer.naturalHeight;
    ctx.drawImage(dataLayer, 0, 0);
  
    const rect = dataLayer.getBoundingClientRect();
    const scaleX = dataLayer.naturalWidth / rect.width;
    const scaleY = dataLayer.naturalHeight / rect.height;
  
    const x = Math.floor((event.clientX - rect.left) * scaleX);
    const y = Math.floor((event.clientY - rect.top) * scaleY);
  
    const pixel = ctx.getImageData(x, y, 1, 1).data;
    const clickedColor = [pixel[0], pixel[1], pixel[2]];
  
    let found = false;
    for (const colorKey in genreColors) {
      const refColor = colorKey.split(',').map(Number);
      if (isSimilarColor(clickedColor, refColor, 50)) {
        const genre = genreColors[colorKey];
        showInfoBox(event, genre, currentDecade);
        found = true;
        break;
      }
    }
  
    if (!found) {
      hideInfoBox();
    }
  });

  // Inicialització
  toggleElements.checked = false;
  document.getElementById('elements').style.display = 'none';
  opacitySlider.value = 0;
  opacityElement.classList.add('hidden');
  document.getElementById('data').style.opacity = 1;
  updateButtonsState();
});