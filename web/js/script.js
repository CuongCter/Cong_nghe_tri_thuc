// Data Science Salary Analysis Dashboard JavaScript

// Job title mapping for encoding
const JOB_MAPPING = {
  "Data Engineer": 0,
  "Data Scientist": 1,
  "Data Analyst": 2,
  "Data Architect": 3,
  "Data Science": 4,
  "Data Manager": 5,
  "Data Science Manager": 6,
  "Data Specialist": 7,
  "Data Science Consultant": 8,
  "Data Analytics Manager": 9,
  "Head of Data": 10,
  "Data Modeler": 11,
  "Data Product Manager": 12,
  "Director of Data Science": 13,
};

// Model coefficients (from the trained model)
const MODEL_COEFFICIENTS = {
  intercept: 136913.07,
  work_year: 2635.11,
  experience_level_encoded: 14263.28,
  employment_type_encoded: -67.69,
  job_title_encoded: 11506.27,
  remote_ratio: 293.69,
  company_size_encoded: -1651.69,
  is_us: 15282.33,
};

// Initialize the application
document.addEventListener("DOMContentLoaded", function () {
  initializeApp();
});

function initializeApp() {
  // Initialize remote ratio slider
  initializeRemoteSlider();

  // Initialize prediction form
  initializePredictionForm();

  // Initialize smooth scrolling
  initializeSmoothScrolling();

  // Initialize chart image modals
  initializeChartModals();

  // Initialize navbar scroll effect
  initializeNavbarScroll();
}

// Remote ratio slider functionality
function initializeRemoteSlider() {
  const remoteSlider = document.getElementById("remoteRatio");
  const remoteValue = document.getElementById("remoteValue");

  if (remoteSlider && remoteValue) {
    remoteSlider.addEventListener("input", function () {
      remoteValue.textContent = this.value + "%";
    });
  }
}

// Prediction form functionality
function initializePredictionForm() {
  const form = document.getElementById("salaryForm");

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      handlePrediction();
    });
  }
}

// Handle salary prediction
function handlePrediction() {
  // Show loading state
  showLoadingState();

  // Get form data
  const formData = getFormData();

  // Call API instead of local calculation
  fetch("/api/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(formData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        throw new Error(data.error);
      }
      // Display result
      displayPredictionResult(data, formData);
    })
    .catch((error) => {
      console.error("Error:", error);
      // Fallback to local calculation
      setTimeout(() => {
        const prediction = calculateSalaryPrediction(formData);
        displayPredictionResult(prediction, formData);
      }, 500);
    });
}

// Make function available globally for onclick
window.handlePrediction = handlePrediction;

// Get form data
function getFormData() {
  try {
    return {
      work_year: 2024, // Fixed year
      experience_level:
        document.getElementById("experienceLevel")?.value || "EN",
      employment_type: document.getElementById("employmentType")?.value || "FT",
      job_title: document.getElementById("jobTitle")?.value || "Data Engineer",
      remote_ratio: parseInt(
        document.getElementById("remoteRatio")?.value || "50"
      ),
      company_size: document.getElementById("companySize")?.value || "M",
      company_location:
        document.getElementById("companyLocation")?.value || "US",
    };
  } catch (error) {
    console.error("Error getting form data:", error);
    // Return default values
    return {
      work_year: 2024,
      experience_level: "EN",
      employment_type: "FT",
      job_title: "Data Engineer",
      remote_ratio: 50,
      company_size: "M",
      company_location: "US",
    };
  }
}

// Show loading state (using Tailwind loading state)
function showLoadingState() {
  try {
    const loadingElement = document.getElementById("loadingState");
    const outputElement = document.getElementById("predictionOutput");

    if (loadingElement) {
      loadingElement.style.display = "block";
    }
    if (outputElement) {
      outputElement.style.display = "none";
    }
  } catch (error) {
    console.error("Error showing loading state:", error);
  }
}

// Calculate salary prediction using the model
function calculateSalaryPrediction(data) {
  // Encode categorical variables
  const experience_encoded = { EN: 0, MI: 1, SE: 2, EX: 3 }[
    data.experience_level
  ];
  const employment_encoded = { FT: 0, PT: 1, CT: 2, FL: 3 }[
    data.employment_type
  ];
  const job_encoded = JOB_MAPPING[data.job_title];
  const company_size_encoded = { S: 0, M: 1, L: 2 }[data.company_size];
  const is_us = data.company_location === "US" ? 1 : 0;

  // Calculate prediction using linear regression formula
  const prediction =
    MODEL_COEFFICIENTS.intercept +
    MODEL_COEFFICIENTS.work_year * data.work_year +
    MODEL_COEFFICIENTS.experience_level_encoded * experience_encoded +
    MODEL_COEFFICIENTS.employment_type_encoded * employment_encoded +
    MODEL_COEFFICIENTS.job_title_encoded * job_encoded +
    MODEL_COEFFICIENTS.remote_ratio * data.remote_ratio +
    MODEL_COEFFICIENTS.company_size_encoded * company_size_encoded +
    MODEL_COEFFICIENTS.is_us * is_us;

  // Calculate confidence interval (±37,641 MAE)
  const mae = 37641;
  const confidence_lower = Math.max(0, prediction - mae);
  const confidence_upper = prediction + mae;

  return {
    prediction: Math.round(prediction),
    confidence_lower: Math.round(confidence_lower),
    confidence_upper: Math.round(confidence_upper),
  };
}

// Display prediction result
function displayPredictionResult(result, formData) {
  const output = document.getElementById("predictionOutput");
  const loadingState = document.getElementById("loadingState");

  if (!output) {
    console.error("predictionOutput element not found");
    return;
  }

  // Hide loading state and show result
  if (loadingState) {
    loadingState.style.display = "none";
  }
  output.style.display = "block";

  // Format numbers with commas
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Handle both API response and local calculation
  const prediction = result.prediction || result.predicted_salary;
  const confidence_lower = result.confidence_lower || result.lower_bound;
  const confidence_upper = result.confidence_upper || result.upper_bound;
  const method = result.method || "local_calculation";

  // Create result HTML
  output.innerHTML = `
        <div class="text-center space-y-6">
            <!-- Main Salary Display -->
            <div class="space-y-2">
                <div class="text-5xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
                    ${formatCurrency(prediction)}
                </div>
                <div class="text-lg text-gray-600">
                    Dự đoán mức lương năm 2024
                </div>
            </div>

            <!-- Confidence Interval -->
            <div class="bg-gradient-to-r from-blue-50 to-green-50 rounded-xl p-4 border border-blue-200">
                <div class="text-sm font-semibold text-gray-700 mb-2">
                    <i class="fas fa-chart-line text-blue-600 mr-2"></i>
                    Khoảng tin cậy 95%
                </div>
                <div class="text-lg font-bold text-gray-800">
                    ${formatCurrency(confidence_lower)} - ${formatCurrency(
    confidence_upper
  )}
                </div>
                <div class="text-xs text-gray-500 mt-1">
                    MAE: ±${formatCurrency(37641)}
                </div>
            </div>

            <!-- Details Grid -->
            <div class="grid grid-cols-2 gap-4 text-left">
                <div class="bg-gray-50 rounded-lg p-3">
                    <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Job Title</div>
                    <div class="text-sm font-bold text-gray-900 mt-1">${
                      formData.job_title
                    }</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-3">
                    <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Experience</div>
                    <div class="text-sm font-bold text-gray-900 mt-1">${
                      formData.experience_level
                    }</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-3">
                    <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Location</div>
                    <div class="text-sm font-bold text-gray-900 mt-1">${
                      formData.company_location
                    }</div>
                </div>
                <div class="bg-gray-50 rounded-lg p-3">
                    <div class="text-xs font-semibold text-gray-500 uppercase tracking-wide">Remote</div>
                    <div class="text-sm font-bold text-gray-900 mt-1">${
                      formData.remote_ratio
                    }%</div>
                </div>
            </div>

            <!-- Method Badge -->
            <div class="flex justify-center">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                  method === "trained_model"
                    ? "bg-green-100 text-green-800"
                    : "bg-yellow-100 text-yellow-800"
                }">
                    <i class="fas fa-${
                      method === "trained_model" ? "robot" : "calculator"
                    } mr-1"></i>
                    ${
                      method === "trained_model"
                        ? "ML Model"
                        : "Fallback Calculation"
                    }
                </span>
            </div>

            <!-- Action Button -->
            <div class="pt-4">
                <button onclick="handlePrediction()" class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transform hover:scale-105 transition-all duration-200 shadow-lg">
                    <i class="fas fa-redo mr-2"></i>
                    Tính lại
                </button>
            </div>
        </div>
    `;

  // Add animation
  if (output) {
    output.style.opacity = "0";
    setTimeout(() => {
      output.style.transition = "opacity 0.5s ease";
      output.style.opacity = "1";
    }, 100);
  }
}

// Smooth scrolling for navigation links
function initializeSmoothScrolling() {
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
}

// Chart image modals
function initializeChartModals() {
  // Add click handlers to all chart images
  document.querySelectorAll('img[src*="images/"]').forEach((img) => {
    img.style.cursor = "pointer";
    img.addEventListener("click", function () {
      openImageModal(this.src, this.alt);
    });
  });
}

// Open image in modal
function openImageModal(src, alt) {
  // Create Tailwind modal HTML
  const modalHTML = `
    <div id="imageModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75 backdrop-blur-sm">
      <div class="relative max-w-7xl max-h-screen mx-4 bg-white rounded-2xl shadow-2xl overflow-hidden">
        <!-- Header -->
        <div class="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <h3 class="text-xl font-bold text-gray-900">${alt}</h3>
          <button onclick="closeImageModal()" class="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors">
            <i class="fas fa-times text-gray-600 text-lg"></i>
          </button>
        </div>

        <!-- Image Container -->
        <div class="p-6 max-h-[80vh] overflow-auto">
          <img src="${src}" alt="${alt}" class="w-full h-auto rounded-lg shadow-lg">
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div class="text-sm text-gray-600">
            <i class="fas fa-info-circle mr-2"></i>
            Click outside or press ESC to close
          </div>
          <button onclick="closeImageModal()" class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            <i class="fas fa-times mr-2"></i>Close
          </button>
        </div>
      </div>
    </div>
  `;

  // Remove existing modal
  const existingModal = document.getElementById("imageModal");
  if (existingModal) {
    existingModal.remove();
  }

  // Add modal to body
  document.body.insertAdjacentHTML("beforeend", modalHTML);

  // Add event listeners
  const modal = document.getElementById("imageModal");

  // Close on background click
  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      closeImageModal();
    }
  });

  // Close on ESC key
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      closeImageModal();
    }
  });

  // Prevent body scroll
  document.body.style.overflow = "hidden";
}

// Close image modal
function closeImageModal() {
  const modal = document.getElementById("imageModal");
  if (modal) {
    modal.remove();
  }

  // Restore body scroll
  document.body.style.overflow = "";

  // Remove ESC key listener
  document.removeEventListener("keydown", closeImageModal);
}

// Make functions available globally
window.openImageModal = openImageModal;
window.closeImageModal = closeImageModal;

// Navbar scroll effect
function initializeNavbarScroll() {
  window.addEventListener("scroll", function () {
    const navbar = document.querySelector("nav");
    if (navbar && window.scrollY > 100) {
      navbar.style.backgroundColor = "rgba(255, 255, 255, 0.95)";
      navbar.style.backdropFilter = "blur(10px)";
    } else if (navbar) {
      navbar.style.backgroundColor = "rgba(255, 255, 255, 0.8)";
      navbar.style.backdropFilter = "blur(10px)";
    }
  });
}

// Update active nav link based on scroll position
function updateActiveNavLink() {
  const sections = document.querySelectorAll("section[id]");
  const navLinks = document.querySelectorAll(".nav-link");

  let current = "";
  sections.forEach((section) => {
    const sectionTop = section.offsetTop;
    if (window.scrollY >= sectionTop - 200) {
      current = section.getAttribute("id");
    }
  });

  navLinks.forEach((link) => {
    link.classList.remove("active");
    if (link.getAttribute("href") === `#${current}`) {
      link.classList.add("active");
    }
  });
}

// Add scroll listener for active nav link
window.addEventListener("scroll", updateActiveNavLink);

// Utility function to format numbers
function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  } else if (num >= 1000) {
    return (num / 1000).toFixed(0) + "K";
  }
  return num.toString();
}

// Add some interactive animations
function addInteractiveAnimations() {
  // Animate stats on scroll
  const observerOptions = {
    threshold: 0.5,
    rootMargin: "0px 0px -100px 0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.animation = "fadeInUp 0.6s ease forwards";
      }
    });
  }, observerOptions);

  // Observe stat cards and feature cards
  document
    .querySelectorAll(".stat-card, .feature-card, .insight-card")
    .forEach((card) => {
      observer.observe(card);
    });
}

// Initialize animations when DOM is loaded
document.addEventListener("DOMContentLoaded", addInteractiveAnimations);

// Add CSS animation keyframes dynamically
const style = document.createElement("style");
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    .rule-card { animation: slideIn 0.4s ease-out; }
`;
document.head.appendChild(style);

// ============================================================
// EXPERT SYSTEM - Hệ Chuyên Gia Tư Vấn Lương
// ============================================================

// Xử lý form Expert System
async function handleExpertSystem() {
    const loadingEl = document.getElementById('expertLoading');
    const outputEl = document.getElementById('expertOutput');

    // Lấy dữ liệu form
    const formData = {
        work_year: 2024,
        experience_level: document.getElementById('ex_experienceLevel').value,
        employment_type: document.getElementById('ex_employmentType').value,
        job_title: document.getElementById('ex_jobTitle').value,
        remote_ratio: parseInt(document.getElementById('ex_remoteRatio').value),
        company_size: document.getElementById('ex_companySize').value,
        company_location: document.getElementById('ex_companyLocation').value
    };

    // Show loading
    loadingEl.classList.remove('hidden');
    outputEl.innerHTML = '';

    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        if (data.error) throw new Error(data.error);

        // Render kết quả
        renderExpertResult(data);
    } catch (err) {
        console.error('Expert System error:', err);
        outputEl.innerHTML = `
            <div class="text-center py-8 text-red-500">
                <i class="fas fa-exclamation-circle text-3xl mb-3"></i>
                <p>Lỗi: ${err.message}</p>
            </div>
        `;
    } finally {
        loadingEl.classList.add('hidden');
    }
}

// Render kết quả từ Expert System
function renderExpertResult(data) {
    const rec = data.recommendation || {};
    const expl = data.explanation || {};
    const display = data.display || {};
    const meta = data.metadata || {};

    const ml = rec.ml_prediction || {};
    const rules = rec.rules_fired || [];
    const drivers = rec.key_drivers || [];

    // Header với tier và confidence
    let html = `
        <div class="space-y-6">
            <!-- Header: Tier & Confidence -->
            <div class="bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl p-6">
                <div class="flex items-center justify-between mb-3">
                    <span class="px-3 py-1 bg-white text-purple-700 text-xs font-bold rounded-full">
                        <i class="fas fa-brain mr-1"></i>EXPERT SYSTEM
                    </span>
                    <span class="text-sm text-gray-600">
                        <i class="fas fa-check-circle text-green-500 mr-1"></i>
                        ${rules.length}/${meta.rules_total} luật kích hoạt
                    </span>
                </div>
                <h4 class="text-2xl font-bold text-gray-900 mb-2">
                    ${rec.tier || 'Standard Tier'}
                </h4>
                <div class="flex items-center text-sm text-gray-600">
                    <i class="fas fa-chart-pie mr-2 text-purple-600"></i>
                    Overall Confidence:
                    <span class="ml-2 px-2 py-1 bg-white rounded-full font-bold ${(rec.overall_confidence >= 0.8) ? 'text-green-600' : (rec.overall_confidence >= 0.6 ? 'text-yellow-600' : 'text-red-600')}">
                        ${((rec.overall_confidence || 0) * 100).toFixed(0)}%
                    </span>
                </div>
            </div>

            <!-- Mức lương dự đoán -->
            <div class="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-xl p-6 text-center">
                <div class="text-sm text-gray-600 mb-1">Mức lương đề xuất</div>
                <div class="text-4xl font-bold text-green-700 mb-2">
                    $${(ml.prediction || 0).toLocaleString()}
                </div>
                <div class="text-sm text-gray-600">
                    Khoảng chấp nhận được (±MAE):
                    <span class="font-semibold text-gray-800">
                        $${(ml.confidence_lower || 0).toLocaleString()} - $${(ml.confidence_upper || 0).toLocaleString()}
                    </span>
                </div>
            </div>
    `;

    // Warnings (nếu có)
    if (rec.warnings && rec.warnings.length > 0) {
        html += `
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-xl">
                <div class="font-semibold text-yellow-800 mb-2">
                    <i class="fas fa-exclamation-triangle mr-2"></i>Cảnh báo
                </div>
                <ul class="text-sm text-yellow-700 space-y-1">
                    ${rec.warnings.map(w => `<li>• ${w}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // Strategy
    if (rec.strategy) {
        const s = rec.strategy;
        html += `
            <div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-xl">
                <div class="font-semibold text-blue-800 mb-2">
                    <i class="fas fa-bullseye mr-2"></i>Chiến lược tuyển dụng
                </div>
                <div class="text-sm text-blue-700 space-y-1">
                    ${s.strategy ? `<div><strong>Chiến lược:</strong> ${s.strategy}</div>` : ''}
                    ${s.suggested_recruitment_time ? `<div><strong>Thời gian:</strong> ${s.suggested_recruitment_time}</div>` : ''}
                    ${s.suggested_bonus ? `<div><strong>Bonus:</strong> ${s.suggested_bonus}</div>` : ''}
                    ${s.urgency ? `<div><strong>Khẩn cấp:</strong> ${s.urgency}</div>` : ''}
                    ${s.benefits_to_highlight ? `<div><strong>Benefits:</strong> ${s.benefits_to_highlight.join(', ')}</div>` : ''}
                </div>
            </div>
        `;
    }

    // Luật đã kích hoạt
    if (rules.length > 0) {
        html += `
            <div>
                <div class="font-bold text-gray-900 mb-3 flex items-center">
                    <i class="fas fa-gavel text-purple-600 mr-2"></i>
                    Luật chuyên gia được kích hoạt (${rules.length})
                </div>
                <div class="space-y-2 max-h-96 overflow-y-auto pr-2">
        `;

        rules.forEach((rule, idx) => {
            const cfClass = (rule.cf >= 0.85) ? 'bg-green-100 text-green-700' :
                            (rule.cf >= 0.7) ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700';
            const messageHtml = formatRuleMessage(rule.then);
            html += `
                <div class="rule-card bg-white border border-gray-200 rounded-lg p-3 hover:shadow-md transition-shadow">
                    <div class="flex items-center justify-between mb-2">
                        <span class="text-xs font-mono text-gray-500">${rule.rule_id}</span>
                        <span class="px-2 py-0.5 text-xs font-bold rounded-full ${cfClass}">
                            CF: ${(rule.cf * 100).toFixed(0)}%
                        </span>
                    </div>
                    <div class="text-sm font-semibold text-gray-800 mb-1">${rule.description}</div>
                    <div class="text-xs text-gray-600 mb-1">
                        <i class="fas fa-tag mr-1"></i>${rule.category}
                    </div>
                    <div class="text-xs text-gray-700 mt-2 bg-gray-50 p-2 rounded">
                        ${messageHtml}
                    </div>
                </div>
            `;
        });

        html += `</div></div>`;
    }

    // Key Drivers
    if (drivers && drivers.length > 0) {
        html += `
            <div class="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl p-4">
                <div class="font-bold text-gray-900 mb-3 flex items-center">
                    <i class="fas fa-chart-line text-indigo-600 mr-2"></i>Yếu tố chính
                </div>
                <div class="space-y-2">
        `;
        drivers.forEach(d => {
            html += `
                <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-700"><i class="fas fa-circle text-indigo-400 text-xs mr-2"></i>${d.factor}</span>
                    <span class="font-bold ${d.impact.startsWith('+') ? 'text-green-600' : (d.impact.startsWith('-') ? 'text-red-600' : 'text-gray-600')}">
                        ${d.impact}
                    </span>
                </div>
            `;
        });
        html += `</div></div>`;
    }

    // Market context
    if (expl.market_context) {
        const m = expl.market_context;
        html += `
            <div class="bg-orange-50 rounded-xl p-4">
                <div class="font-bold text-gray-900 mb-2 flex items-center">
                    <i class="fas fa-globe text-orange-600 mr-2"></i>So sánh thị trường
                </div>
                <div class="text-sm space-y-1">
                    <div class="flex justify-between">
                        <span class="text-gray-600">vs Market Avg ($136,854):</span>
                        <span class="font-bold ${m.vs_average.amount >= 0 ? 'text-green-600' : 'text-red-600'}">
                            ${m.vs_average.formatted}
                        </span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-600">vs Market Median ($133,000):</span>
                        <span class="font-bold ${m.vs_median.amount >= 0 ? 'text-green-600' : 'text-red-600'}">
                            ${m.vs_median.formatted}
                        </span>
                    </div>
                    <div class="text-gray-700 mt-2 text-xs italic">
                        ${m.market_summary} • ${m.percentile_estimate}
                    </div>
                </div>
            </div>
        `;
    }

    // Action items
    const actions = rec.actions || [];
    if (actions.length > 0 || (rec.negotiation_tips && rec.negotiation_tips.length > 0)) {
        html += `
            <div class="bg-gradient-to-r from-emerald-50 to-green-50 rounded-xl p-4">
                <div class="font-bold text-gray-900 mb-2 flex items-center">
                    <i class="fas fa-tasks text-emerald-600 mr-2"></i>Hành động đề xuất
                </div>
                <ul class="text-sm space-y-1 text-gray-700">
        `;
        actions.forEach(a => {
            html += `<li class="flex items-start"><i class="fas fa-check text-emerald-500 mr-2 mt-1"></i><span>${a}</span></li>`;
        });
        if (rec.negotiation_tips) {
            rec.negotiation_tips.forEach(t => {
                html += `<li class="flex items-start"><i class="fas fa-comments text-blue-500 mr-2 mt-1"></i><span>${t}</span></li>`;
            });
        }
        html += `</ul></div>`;
    }

    html += `</div>`;
    document.getElementById('expertOutput').innerHTML = html;
}

// Helper: format rule then-message
function formatRuleMessage(then) {
    if (!then) return '';
    const parts = [];
    if (then.tier) parts.push(`<strong>${then.tier}</strong>`);
    if (then.salary_range && Array.isArray(then.salary_range)) {
        parts.push(`Khoảng: $${then.salary_range[0].toLocaleString()} - $${then.salary_range[1].toLocaleString()}`);
    }
    if (then.market_position) parts.push(`Vị thế: ${then.market_position}`);
    if (then.action) parts.push(`<em>${then.action}</em>`);
    if (then.warning) parts.push(`<span class="text-yellow-700">⚠️ ${then.warning}</span>`);
    if (then.strategy) parts.push(`<em>${then.strategy}</em>`);
    if (then.suggested_recruitment_time) parts.push(`⏱️ ${then.suggested_recruitment_time}`);
    if (then.suggested_bonus) parts.push(`💰 ${then.suggested_bonus}`);
    if (then.benefits_to_highlight) parts.push(`✨ ${then.benefits_to_highlight.join(', ')}`);
    if (then.characteristic) parts.push(`<em>${then.characteristic}</em>`);
    if (then.salary_adjustment) parts.push(`📊 ${then.salary_adjustment}`);
    if (then.general_advice) parts.push(`<em>${then.general_advice}</em>`);
    if (then.salary_negotiation_tips) parts.push(`Tips: ${then.salary_negotiation_tips.join('; ')}`);
    return parts.join(' • ');
}

// Khởi tạo slider cho expert form
document.addEventListener('DOMContentLoaded', function() {
    const exSlider = document.getElementById('ex_remoteRatio');
    const exValue = document.getElementById('ex_remoteValue');
    if (exSlider && exValue) {
        exSlider.addEventListener('input', function() {
            exValue.textContent = this.value;
        });
    }

    // Format salary input cho backward chaining form
    const salaryInput = document.getElementById('rev_targetSalary');
    const salaryFormatted = document.getElementById('rev_salaryFormatted');
    if (salaryInput && salaryFormatted) {
        salaryInput.addEventListener('input', function() {
            const val = parseInt(this.value) || 0;
            salaryFormatted.textContent = '$' + val.toLocaleString();
        });
    }
});

// ============================================================
// BACKWARD CHAINING - Tìm vị trí theo ngân sách
// ============================================================

async function handleReverseInference() {
    const loadingEl = document.getElementById('reverseLoading');
    const outputEl = document.getElementById('reverseOutput');

    const targetSalary = parseInt(document.getElementById('rev_targetSalary').value);
    if (!targetSalary || targetSalary < 30000) {
        outputEl.innerHTML = `
            <div class="text-center py-8 text-red-500">
                <i class="fas fa-exclamation-circle text-3xl mb-3"></i>
                <p>Vui lòng nhập ngân sách hợp lệ (>= $30,000)</p>
            </div>`;
        return;
    }

    const constraints = {
        target_salary: targetSalary,
        company_location: document.getElementById('rev_location').value || null,
        employment_type: document.getElementById('rev_employment').value || null,
        remote_ratio: document.getElementById('rev_remote').value !== '' ?
                       parseInt(document.getElementById('rev_remote').value) : null,
        top_k: 5
    };

    loadingEl.classList.remove('hidden');
    outputEl.innerHTML = '';

    try {
        const response = await fetch('/api/recommend-reverse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(constraints)
        });

        const data = await response.json();
        if (data.error) throw new Error(data.error);

        renderReverseResults(data);
    } catch (err) {
        console.error('Reverse inference error:', err);
        outputEl.innerHTML = `
            <div class="text-center py-8 text-red-500">
                <i class="fas fa-exclamation-circle text-3xl mb-3"></i>
                <p>Lỗi: ${err.message}</p>
            </div>`;
    } finally {
        loadingEl.classList.add('hidden');
    }
}

function renderReverseResults(data) {
    const r = data.recommendations || {};
    const candidates = r.candidates || [];
    const outputEl = document.getElementById('reverseOutput');

    if (candidates.length === 0) {
        outputEl.innerHTML = `
            <div class="text-center py-8 text-yellow-600">
                <i class="fas fa-search-minus text-3xl mb-3"></i>
                <p>Không tìm thấy vị trí phù hợp trong khoảng ±20%</p>
                <p class="text-sm mt-2">Hãy thử điều chỉnh ngân sách hoặc nới lỏng ràng buộc</p>
            </div>`;
        return;
    }

    const target = r.target_salary;
    const min = r.min_salary;
    const max = r.max_salary;

    let html = `
        <div class="space-y-4">
            <!-- Summary -->
            <div class="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-xl p-4 border border-yellow-200">
                <div class="text-xs text-gray-600 mb-1">Đã tìm thấy</div>
                <div class="text-2xl font-bold text-yellow-700">
                    ${r.unique_profiles} profiles
                </div>
                <div class="text-xs text-gray-500 mt-1">
                    Trong khoảng <strong>$${min.toLocaleString()} - $${max.toLocaleString()}</strong>
                    (đánh giá ${r.evaluated} combinations)
                </div>
            </div>

            <!-- Candidates List -->
            <div class="space-y-3 max-h-96 overflow-y-auto pr-2">
    `;

    candidates.forEach((c, idx) => {
        const accuracy = c.distance_from_target;
        const accuracyClass = accuracy === 0 ? 'text-green-600' :
                              accuracy < 5000 ? 'text-blue-600' :
                              'text-gray-600';

        html += `
            <div class="bg-white border-2 border-gray-200 hover:border-yellow-400 rounded-xl p-4 transition-all">
                <div class="flex items-start justify-between mb-2">
                    <div>
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 bg-yellow-100 text-yellow-800 text-xs font-bold rounded">
                                #${idx + 1}
                            </span>
                            <span class="px-2 py-0.5 bg-purple-100 text-purple-800 text-xs font-bold rounded">
                                ${c.experience_level}
                            </span>
                        </div>
                        <div class="font-bold text-gray-900 mt-1">
                            ${c.job_title}
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-lg font-bold text-green-700">
                            $${c.predicted_salary.toLocaleString()}
                        </div>
                        <div class="text-xs ${accuracyClass}">
                            ${accuracy === 0 ? '✓ Chính xác' : '±' + accuracy.toLocaleString()}
                        </div>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs text-gray-600 mt-2">
                    <div>
                        <i class="fas fa-globe text-blue-500 mr-1"></i>
                        ${c.company_location === 'US' ? 'United States' : 'Non-US'}
                    </div>
                    <div>
                        <i class="fas fa-building text-purple-500 mr-1"></i>
                        Company: ${c.company_size === 'S' ? 'Small' : c.company_size === 'M' ? 'Medium' : 'Large'}
                    </div>
                    <div>
                        <i class="fas fa-clock text-red-500 mr-1"></i>
                        ${c.employment_type}
                    </div>
                    <div>
                        <i class="fas fa-home text-indigo-500 mr-1"></i>
                        ${c.remote_ratio}% remote
                    </div>
                </div>
                ${c.tier ? `
                    <div class="mt-2 text-xs px-2 py-1 bg-gray-50 rounded text-gray-700">
                        <i class="fas fa-tag text-gray-400 mr-1"></i>
                        ${c.tier}
                    </div>
                ` : ''}
            </div>
        `;
    });

    html += `
            </div>
            <div class="text-xs text-gray-500 text-center pt-2">
                <i class="fas fa-info-circle mr-1"></i>
                Kết quả dựa trên ${r.evaluated} combinations, lọc trùng lặp để đa dạng hóa
            </div>
        </div>
    `;

    outputEl.innerHTML = html;
}

// Expose globally
window.handleReverseInference = handleReverseInference;

// Expose globally
window.handleExpertSystem = handleExpertSystem;
