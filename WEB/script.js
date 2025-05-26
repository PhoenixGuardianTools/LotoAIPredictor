async function loadJSON(file) {
  const res = await fetch(file);
  return res.json();
}

function createTable(data) {
  let html = "<table><tr><th>Jeu</th><th>Date</th><th>Numéros</th><th>Gain</th></tr>";
  data.forEach(row => {
    html += `<tr>
      <td>${row.jeu}</td>
      <td>${row.date}</td>
      <td>${row.numeros}</td>
      <td>${row.gain} €</td>
    </tr>`;
  });
  html += "</table>";
  return html;
}

function createRatioStats(stats) {
  let html = "<table><tr><th>Jeu</th><th>Grilles testées</th><th>Gains (€)</th><th>Coûts (€)</th><th>Net</th></tr>";
  stats.forEach(j => {
    let color = j.net >= 0 ? 'green' : 'red';
    html += `<tr>
      <td>${j.jeu}</td>
      <td>${j.tests}</td>
      <td>${j.gains}</td>
      <td>${j.couts}</td>
      <td style="color:${color}">${j.net} €</td>
    </tr>`;
  });
  html += "</table>";
  return html;
}

function load() {
  loadJSON("stats/performance.json").then(data => {
    document.getElementById("performance").innerText = data.resume;
  });

  loadJSON("stats/tirages_recents.json").then(data => {
    document.getElementById("tirages-table").innerHTML = createTable(data);
  });

  loadJSON("stats/ratio_jeux.json").then(data => {
    document.getElementById("ratio-stats").innerHTML = createRatioStats(data);
  });
}

window.onload = load;
