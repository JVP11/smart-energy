const storageKeys = {
  appliances: "sem_appliances",
  history: "sem_history",
};

function formatCurrency(v) {
  if (isNaN(v)) return "₹0";
  return "₹" + v.toFixed(0);
}

function formatUnits(v) {
  if (isNaN(v)) return "0 kWh";
  return v.toFixed(0) + " kWh";
}

function loadJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function saveJSON(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // ignore
  }
}

// Real-time bill estimator + carbon footprint
function setupEstimator() {
  const tariffInput = document.getElementById("tariff");
  const usageInput = document.getElementById("monthlyUsage");
  const estUnits = document.getElementById("estUnits");
  const estBill = document.getElementById("estBill");
  const carbon = document.getElementById("carbonFootprint");
  const btn = document.getElementById("estimateBtn");

  function recalc() {
    const tariff = parseFloat(tariffInput.value) || 0;
    const usage = parseFloat(usageInput.value) || 0;
    const bill = tariff * usage;
    estUnits.textContent = formatUnits(usage);
    estBill.textContent = formatCurrency(bill);
    const co2 = usage * 0.8;
    carbon.textContent = co2.toFixed(1) + " kg CO₂";
  }

  btn.addEventListener("click", recalc);
  tariffInput.addEventListener("input", recalc);
  usageInput.addEventListener("input", recalc);
  recalc();
}

// Budgeting
function setupBudgeting() {
  const budgetInput = document.getElementById("budget");
  const currentCostInput = document.getElementById("currentCost");
  const remainingEl = document.getElementById("remainingBudget");
  const statusEl = document.getElementById("budgetStatus");
  const btn = document.getElementById("budgetBtn");

  function update() {
    const budget = parseFloat(budgetInput.value) || 0;
    const current = parseFloat(currentCostInput.value) || 0;
    const remaining = budget - current;
    remainingEl.textContent = formatCurrency(Math.max(remaining, 0));

    if (remaining < 0) {
      statusEl.textContent = "Over budget";
      statusEl.style.color = "#fecaca";
    } else if (remaining < budget * 0.2) {
      statusEl.textContent = "Close to limit";
      statusEl.style.color = "#facc15";
    } else {
      statusEl.textContent = "On track";
      statusEl.style.color = "#bbf7d0";
    }
  }

  btn.addEventListener("click", update);
  budgetInput.addEventListener("input", update);
  currentCostInput.addEventListener("input", update);
  update();
}

// Appliances + alerts + recommendations
function setupAppliances() {
  const tableBody = document.getElementById("applianceTableBody");
  const alertsContainer = document.getElementById("alerts");
  const recList = document.getElementById("recommendations");
  const form = document.getElementById("applianceForm");
  const nameInput = document.getElementById("applianceName");
  const unitsInput = document.getElementById("applianceUnits");
  const tariffInput = document.getElementById("tariff");

  let appliances = loadJSON(storageKeys.appliances, [
    { name: "AC", units: 120 },
    { name: "Refrigerator", units: 45 },
    { name: "TV", units: 20 },
  ]);

  function render() {
    const tariff = parseFloat(tariffInput.value) || 0;
    tableBody.innerHTML = "";
    alertsContainer.innerHTML = "";
    appliances.forEach((appliance) => {
      const cost = appliance.units * tariff;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${appliance.name}</td>
        <td>${appliance.units.toFixed(1)}</td>
        <td>${formatCurrency(cost)}</td>
      `;
      tableBody.appendChild(tr);

      if (appliance.units >= 80) {
        const alert = document.createElement("div");
        alert.className = "alert alert-high";
        alert.textContent = `⚠ High energy usage: ${appliance.name} has consumed ${appliance.units.toFixed(
          1
        )} kWh this month. Consider reducing hours or increasing temperature.`;
        alertsContainer.appendChild(alert);
      }
    });

    if (!appliances.some((a) => a.units >= 80)) {
      const ok = document.createElement("div");
      ok.className = "alert alert-ok";
      ok.textContent = "✅ No high-usage appliances detected this month.";
      alertsContainer.appendChild(ok);
    }

    const recs = [];
    if (appliances.some((a) => a.name.toLowerCase().includes("bulb"))) {
      recs.push("Replace incandescent bulbs with LED bulbs.");
    }
    if (appliances.some((a) => a.name.toLowerCase().includes("ac"))) {
      recs.push("Use AC at 24°C and limit hours during peak times.");
    }
    recs.push(
      "Turn off appliances completely instead of leaving them on standby."
    );

    recList.innerHTML = "";
    recs.forEach((r) => {
      const li = document.createElement("li");
      li.textContent = r;
      recList.appendChild(li);
    });
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const name = nameInput.value.trim();
    const units = parseFloat(unitsInput.value);
    if (!name || isNaN(units)) return;
    appliances.push({ name, units });
    saveJSON(storageKeys.appliances, appliances);
    nameInput.value = "";
    unitsInput.value = "";
    render();
  });

  tariffInput.addEventListener("input", render);
  render();
}

// Appliance comparison & planner use same tariff
function setupComparisonAndPlanner() {
  const form = document.getElementById("compareForm");
  const result = document.getElementById("compareResult");
  const tariffInput = document.getElementById("tariff");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const aName = document.getElementById("applianceAName").value.trim();
    const aPower = parseFloat(
      document.getElementById("applianceAPower").value
    );
    const bName = document.getElementById("applianceBName").value.trim();
    const bPower = parseFloat(
      document.getElementById("applianceBPower").value
    );
    const hours = parseFloat(document.getElementById("hoursPerDay").value);
    const days = parseFloat(document.getElementById("daysPerMonth").value);
    const tariff = parseFloat(tariffInput.value) || 0;
    if (
      !aName ||
      !bName ||
      [aPower, bPower, hours, days].some((v) => isNaN(v))
    ) {
      return;
    }
    const kWhA = (aPower * hours * days) / 1000;
    const kWhB = (bPower * hours * days) / 1000;
    const costA = kWhA * tariff;
    const costB = kWhB * tariff;
    const diff = costB - costA;
    const better = diff > 0 ? aName : bName;
    const save = Math.abs(diff);

    result.textContent = `${better} is cheaper by about ${formatCurrency(
      save
    )} per month for the given usage.`;
  });

  // Planner
  const plannerPower = document.getElementById("plannerPower");
  const plannerHours = document.getElementById("plannerHours");
  const plannerDays = document.getElementById("plannerDays");
  const plannerBtn = document.getElementById("plannerBtn");
  const plannerUnits = document.getElementById("plannerUnits");
  const plannerCost = document.getElementById("plannerCost");

  function recalcPlanner() {
    const power = parseFloat(plannerPower.value) || 0;
    const hours = parseFloat(plannerHours.value) || 0;
    const days = parseFloat(plannerDays.value) || 0;
    const tariff = parseFloat(tariffInput.value) || 0;
    const kWh = (power * hours * days) / 1000;
    const cost = kWh * tariff;
    plannerUnits.textContent = formatUnits(kWh);
    plannerCost.textContent = formatCurrency(cost);
  }

  plannerBtn.addEventListener("click", recalcPlanner);
  [plannerPower, plannerHours, plannerDays, tariffInput].forEach((el) =>
    el.addEventListener("input", recalcPlanner)
  );
  recalcPlanner();
}

// History / trends
function setupHistory() {
  const form = document.getElementById("historyForm");
  const monthInput = document.getElementById("historyMonth");
  const unitsInput = document.getElementById("historyUnits");
  const billInput = document.getElementById("historyBill");
  const tableBody = document.getElementById("historyTableBody");

  let history = loadJSON(storageKeys.history, [
    { month: "Jan", units: 150, bill: 1200 },
    { month: "Feb", units: 130, bill: 1040 },
    { month: "Mar", units: 180, bill: 1440 },
  ]);

  function render() {
    tableBody.innerHTML = "";
    history.forEach((item) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${item.month}</td>
        <td>${item.units}</td>
        <td>${formatCurrency(item.bill)}</td>
      `;
      tableBody.appendChild(tr);
    });
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const month = monthInput.value.trim();
    const units = parseFloat(unitsInput.value);
    const bill = parseFloat(billInput.value);
    if (!month || isNaN(units) || isNaN(bill)) return;
    const existing = history.find((h) => h.month.toLowerCase() === month.toLowerCase());
    if (existing) {
      existing.units = units;
      existing.bill = bill;
    } else {
      history.push({ month, units, bill });
    }
    saveJSON(storageKeys.history, history);
    render();
  });

  render();
}

// Smart appliance recommendation
function setupSmartRecommendation() {
  const form = document.getElementById("smartForm");
  const result = document.getElementById("smartResult");
  const tariffInput = document.getElementById("tariff");

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const name = document.getElementById("smartName").value.trim();
    const oldPower = parseFloat(
      document.getElementById("smartOldPower").value
    );
    const newPower = parseFloat(
      document.getElementById("smartNewPower").value
    );
    const hours = parseFloat(document.getElementById("smartHours").value);
    const days = parseFloat(document.getElementById("smartDays").value);
    const tariff = parseFloat(tariffInput.value) || 0;
    if (
      !name ||
      [oldPower, newPower, hours, days].some((v) => isNaN(v)) ||
      oldPower <= newPower
    ) {
      result.textContent =
        "Enter valid values. Old power should be higher than efficient power.";
      return;
    }
    const oldKWh = (oldPower * hours * days) / 1000;
    const newKWh = (newPower * hours * days) / 1000;
    const savingKWh = oldKWh - newKWh;
    const savingCost = savingKWh * tariff;
    result.textContent = `Upgrading your ${name} could save about ${formatCurrency(
      savingCost
    )} per month (${savingKWh.toFixed(1)} kWh).`;
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupEstimator();
  setupBudgeting();
  setupAppliances();
  setupComparisonAndPlanner();
  setupHistory();
  setupSmartRecommendation();
});

