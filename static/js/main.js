(function () {
    const root = document.documentElement;
    const themeToggle = document.getElementById("themeToggle");
    const storedTheme = localStorage.getItem("site-theme");

    const applyTheme = (theme) => {
        root.setAttribute("data-theme", theme);
        localStorage.setItem("site-theme", theme);
    };

    applyTheme(storedTheme || "dark");

    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            const current = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
            applyTheme(current);
        });
    }

    const showToast = (message, timeout = 3800) => {
        const toast = document.getElementById("toast");
        if (!toast) {
            return;
        }
        toast.textContent = message;
        toast.classList.add("show");
        window.setTimeout(() => toast.classList.remove("show"), timeout);
    };

    const revealItems = document.querySelectorAll(".reveal");
    if (revealItems.length > 0) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("active");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.15 }
        );
        revealItems.forEach((item) => observer.observe(item));
    }

    const counters = document.querySelectorAll("[data-counter]");
    if (counters.length > 0) {
        const runCounter = (element) => {
            const target = Number(element.dataset.counter || 0);
            const step = Math.max(1, Math.floor(target / 40));
            let value = 0;
            const update = () => {
                value += step;
                if (value >= target) {
                    element.textContent = String(target);
                    return;
                }
                element.textContent = String(value);
                requestAnimationFrame(update);
            };
            update();
        };

        const counterObserver = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        runCounter(entry.target);
                        counterObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.6 }
        );

        counters.forEach((counter) => counterObserver.observe(counter));
    }

    const pricingButtons = document.querySelectorAll(".pricing-toggle-btn");
    const planCards = document.querySelectorAll(".plan-card");

    const updatePriceMode = (mode) => {
        planCards.forEach((card) => {
            const oneTimePrice = card.dataset.oneTime;
            const monthlyPrice = card.dataset.monthly;
            const target = mode === "monthly" ? monthlyPrice : oneTimePrice;
            const fallback = mode === "monthly" ? oneTimePrice : monthlyPrice;
            const priceNode = card.querySelector("[data-price-text]");
            if (priceNode) {
                priceNode.textContent = target || fallback || "Custom Quote";
            }
        });

        pricingButtons.forEach((btn) => {
            btn.classList.toggle("active", btn.dataset.priceMode === mode);
        });
    };

    pricingButtons.forEach((btn) => {
        btn.addEventListener("click", () => updatePriceMode(btn.dataset.priceMode));
    });

    if (pricingButtons.length > 0) {
        updatePriceMode("one_time");
    }

    const ajaxForms = document.querySelectorAll(".ajax-form");
    ajaxForms.forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const endpoint = form.dataset.endpoint;
            if (!endpoint) {
                return;
            }

            const emailInput = form.querySelector('input[type="email"]');
            if (emailInput && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(emailInput.value.trim())) {
                showToast("Please enter a valid email.");
                return;
            }

            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = "Submitting...";
            }

            try {
                const formData = new FormData(form);
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");
                const response = await fetch(endpoint, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken || "",
                    },
                    body: formData,
                });

                const result = await response.json();
                showToast(result.message || "Request sent.");

                if (result.ok) {
                    form.reset();
                }
            } catch (error) {
                showToast("Unable to submit right now. Please try again.");
            } finally {
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = submitButton.dataset.originalLabel || "Submit";
                }
            }
        });

        const btn = form.querySelector('button[type="submit"]');
        if (btn && !btn.dataset.originalLabel) {
            btn.dataset.originalLabel = btn.textContent;
        }
    });

    const tiltCards = document.querySelectorAll(".tilt-card");
    tiltCards.forEach((card) => {
        card.addEventListener("mousemove", (event) => {
            const rect = card.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            const rotateX = ((y / rect.height) - 0.5) * -8;
            const rotateY = ((x / rect.width) - 0.5) * 10;
            card.style.transform = `perspective(800px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
        card.addEventListener("mouseleave", () => {
            card.style.transform = "perspective(800px) rotateX(0deg) rotateY(0deg)";
        });
    });

    const skeletonCards = document.querySelectorAll(".skeleton img");
    skeletonCards.forEach((img) => {
        if (img.complete) {
            img.closest(".skeleton")?.classList.remove("skeleton");
        } else {
            img.addEventListener("load", () => img.closest(".skeleton")?.classList.remove("skeleton"));
        }
    });
})();
