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

    const planScopes = document.querySelectorAll("[data-plans-scope]");
    planScopes.forEach((scope) => {
        const buttons = scope.querySelectorAll(".pricing-toggle-btn");
        const cards = scope.querySelectorAll("[data-plan-flip]");

        const updateScopeMode = (mode) => {
            buttons.forEach((btn) => {
                btn.classList.toggle("active", btn.dataset.priceMode === mode);
            });
            cards.forEach((card) => {
                card.classList.toggle("is-monthly", mode === "monthly");
            });
        };

        buttons.forEach((btn) => {
            btn.addEventListener("click", () => updateScopeMode(btn.dataset.priceMode));
        });

        updateScopeMode("one_time");
    });

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

    const toolsTrack = document.getElementById("toolsTrack");
    if (toolsTrack) {
        let offset = 0;
        let lastScrollY = window.scrollY;
        let cycleWidth = 0;
        let scrollSpeedFactor = 1.4;
        let rafId = 0;
        let lastFrameTs = 0;
        const autoSpeedPxPerSecond = 34;

        const updateToolsMetrics = () => {
            const firstRow = toolsTrack.querySelector(".tools-row");
            cycleWidth = firstRow ? firstRow.scrollWidth : 0;
            const scrollableHeight = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
            if (cycleWidth > 0) {
                scrollSpeedFactor = Math.max(1.1, (cycleWidth / scrollableHeight) * 2.8);
            }
        };

        const applyToolsTransform = () => {
            if (cycleWidth <= 0) {
                return;
            }
            offset = ((offset % cycleWidth) + cycleWidth) % cycleWidth;
            toolsTrack.style.transform = `translateX(${-offset}px)`;
        };

        const animateToolsTrack = (timestamp) => {
            if (!lastFrameTs) {
                lastFrameTs = timestamp;
            }
            const dt = timestamp - lastFrameTs;
            lastFrameTs = timestamp;

            // Keep strip moving continuously even when page is idle.
            offset += (autoSpeedPxPerSecond * dt) / 1000;
            applyToolsTransform();
            rafId = window.requestAnimationFrame(animateToolsTrack);
        };

        window.addEventListener(
            "scroll",
            () => {
                const currentScrollY = window.scrollY;
                const delta = currentScrollY - lastScrollY;
                lastScrollY = currentScrollY;

                if (delta < 0) {
                    // Scroll up: move tools strip to left
                    offset += Math.abs(delta) * scrollSpeedFactor;
                } else if (delta > 0) {
                    // Scroll down: move to right
                    offset -= delta * scrollSpeedFactor;
                }

                applyToolsTransform();
            },
            { passive: true }
        );

        window.addEventListener("resize", () => {
            updateToolsMetrics();
            applyToolsTransform();
        });

        updateToolsMetrics();
        applyToolsTransform();
        rafId = window.requestAnimationFrame(animateToolsTrack);
    }

    const faqChatToggle = document.getElementById("faqChatToggle");
    const faqChatPanel = document.getElementById("faqChatPanel");
    const faqChatClose = document.getElementById("faqChatClose");
    const faqChatMessages = document.getElementById("faqChatMessages");
    const faqQuickQuestions = document.getElementById("faqQuickQuestions");
    const faqChatForm = document.getElementById("faqChatForm");
    const faqChatInput = document.getElementById("faqChatInput");

    const faqData = [
        {
            question: "What services do you provide?",
            answer: "I provide website development, e-commerce, Python automation, AI chatbot systems, SEO, and maintenance.",
            keywords: ["services", "provide", "offer"],
        },
        {
            question: "What is your tech stack?",
            answer: "My main stack is Python, Flask, PostgreSQL, JavaScript, TailwindCSS, and API integrations.",
            keywords: ["tech", "stack", "flask", "python", "postgresql"],
        },
        {
            question: "Do you work with international clients?",
            answer: "Yes. I work with clients in India and international markets with structured communication and clear milestones.",
            keywords: ["international", "global", "outside india"],
        },
        {
            question: "How long does a website project take?",
            answer: "Most business websites take around 2 to 6 weeks depending on scope, content readiness, and revisions.",
            keywords: ["timeline", "how long", "duration", "weeks"],
        },
        {
            question: "Do you provide maintenance after launch?",
            answer: "Yes. I offer monthly maintenance plans for updates, fixes, monitoring, and performance care.",
            keywords: ["maintenance", "support", "after launch"],
        },
        {
            question: "Can you build e-commerce websites?",
            answer: "Yes. I build custom e-commerce systems with catalog, order flow, payment placeholders, and admin operations.",
            keywords: ["ecommerce", "e-commerce", "store", "shop"],
        },
        {
            question: "Do you offer AI chatbot development?",
            answer: "Yes. I build FAQ bots, smart GPT assistants, and CRM-aware chatbot workflows.",
            keywords: ["chatbot", "ai", "gpt", "assistant"],
        },
        {
            question: "Can you automate repetitive business tasks?",
            answer: "Yes. I create Python automation workflows for lead routing, reporting, data sync, and operations.",
            keywords: ["automation", "script", "workflow", "python"],
        },
        {
            question: "What are your payment terms?",
            answer: "Projects are milestone-based with an advance to start. Final handover happens after full payment.",
            keywords: ["payment", "pricing", "advance", "milestone"],
        },
        {
            question: "Do you provide SEO services?",
            answer: "Yes. I provide technical SEO, on-page optimization, structure improvements, and growth-focused SEO plans.",
            keywords: ["seo", "ranking", "search engine"],
        },
        {
            question: "How can I start a project with you?",
            answer: "Use the Contact or Client Inquiry form, share your goals, and I will respond with scope, timeline, and estimate.",
            keywords: ["start", "hire", "book", "contact"],
        },
        {
            question: "Can I customize one of your plans?",
            answer: "Yes. Plans are a baseline. I can create a custom proposal based on your business and technical needs.",
            keywords: ["custom", "plan", "tailored", "package"],
        },
    ];

    if (faqChatToggle && faqChatPanel && faqChatMessages && faqQuickQuestions && faqChatForm && faqChatInput) {
        const appendFaqMessage = (message, type) => {
            const row = document.createElement("div");
            row.className = `faq-msg ${type === "user" ? "faq-msg-user" : "faq-msg-bot"}`;
            row.textContent = message;
            faqChatMessages.appendChild(row);
            faqChatMessages.scrollTop = faqChatMessages.scrollHeight;
        };

        const findFaqAnswer = (inputText) => {
            const text = (inputText || "").toLowerCase().trim();
            if (!text) {
                return "Please type a question. You can ask about services, pricing, timeline, or support.";
            }
            const match = faqData.find((item) =>
                item.keywords.some((keyword) => text.includes(keyword))
            );
            if (match) {
                return match.answer;
            }
            return "I can help with services, pricing, timeline, automation, AI chatbot, SEO, and maintenance. Use the inquiry form for a detailed quote.";
        };

        const toggleFaqPanel = (isOpen) => {
            faqChatPanel.classList.toggle("open", isOpen);
            faqChatToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
            if (isOpen) {
                faqChatInput.focus();
            }
        };

        appendFaqMessage("Hi, I am your FAQ assistant. Ask me anything about services, pricing, or timeline.", "bot");

        faqData.slice(0, 8).forEach((item) => {
            const chip = document.createElement("button");
            chip.type = "button";
            chip.className = "faq-chip";
            chip.textContent = item.question;
            chip.addEventListener("click", () => {
                appendFaqMessage(item.question, "user");
                window.setTimeout(() => appendFaqMessage(item.answer, "bot"), 220);
                toggleFaqPanel(true);
            });
            faqQuickQuestions.appendChild(chip);
        });

        faqChatToggle.addEventListener("click", () => {
            const next = !faqChatPanel.classList.contains("open");
            toggleFaqPanel(next);
        });

        faqChatClose?.addEventListener("click", () => toggleFaqPanel(false));

        faqChatForm.addEventListener("submit", (event) => {
            event.preventDefault();
            const question = faqChatInput.value.trim();
            if (!question) {
                return;
            }
            appendFaqMessage(question, "user");
            faqChatInput.value = "";
            const answer = findFaqAnswer(question);
            window.setTimeout(() => appendFaqMessage(answer, "bot"), 220);
        });
    }
})();
