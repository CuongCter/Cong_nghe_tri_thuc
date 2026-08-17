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
`;
document.head.appendChild(style);
