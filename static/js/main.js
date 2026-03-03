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

    const scrollTopBtn = document.getElementById("scrollTopBtn");
    if (scrollTopBtn) {
        const toggleScrollTopVisibility = () => {
            scrollTopBtn.classList.toggle("is-visible", window.scrollY > 280);
        };

        scrollTopBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });

        window.addEventListener("scroll", toggleScrollTopVisibility, { passive: true });
        toggleScrollTopVisibility();
    }

    const heroSequenceItems = document.querySelectorAll("#home .hero-seq-item");
    if (heroSequenceItems.length > 0) {
        heroSequenceItems.forEach((item) => {
            const step = Number(item.dataset.heroStep || 0);
            item.style.setProperty("--hero-step", String(step));
        });

        window.requestAnimationFrame(() => {
            window.requestAnimationFrame(() => {
                document.body.classList.add("hero-seq-ready");
            });
        });
    }

    const menuToggles = document.querySelectorAll("[data-menu-target]");
    menuToggles.forEach((toggle) => {
        const menuId = toggle.dataset.menuTarget;
        const menu = document.getElementById(menuId);
        if (!menu) {
            return;
        }

        const setMenuOpen = (isOpen) => {
            toggle.classList.toggle("is-open", isOpen);
            menu.classList.toggle("is-open", isOpen);
            toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        };

        const closeMenu = () => setMenuOpen(false);

        setMenuOpen(false);

        toggle.addEventListener("click", (event) => {
            event.stopPropagation();
            setMenuOpen(!menu.classList.contains("is-open"));
        });

        menu.querySelectorAll("[data-menu-close]").forEach((item) => {
            item.addEventListener("click", closeMenu);
        });

        document.addEventListener("click", (event) => {
            if (!menu.classList.contains("is-open")) {
                return;
            }
            if (!menu.contains(event.target) && !toggle.contains(event.target)) {
                closeMenu();
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                closeMenu();
            }
        });

        window.addEventListener("resize", () => {
            if (window.innerWidth >= 1024) {
                closeMenu();
            }
        });
    });

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

    const aboutSequenceItems = document.querySelectorAll("#about .about-seq-item");
    if (aboutSequenceItems.length > 0) {
        const aboutSection = document.getElementById("about");
        const aboutParagraphItems = Array.from(document.querySelectorAll("#about .about-para-item"));
        const aboutListItems = Array.from(document.querySelectorAll("#about .about-list-item"));
        const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
        const applySequentialVisibility = (items, localProgress) => {
            const count = items.length;
            if (!count) {
                return;
            }
            items.forEach((item, index) => {
                const threshold = (index + 1) / (count + 1);
                item.classList.toggle("is-visible", localProgress >= threshold);
            });
        };

        const updateAboutSequence = () => {
            if (!aboutSection) {
                return;
            }

            const rect = aboutSection.getBoundingClientRect();
            const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 1;

            const start = viewportHeight * 0.9;
            const end = -rect.height * 0.2;
            const totalDistance = Math.max(1, start - end);
            const progress = clamp((start - rect.top) / totalDistance, 0, 1);

            // Delay paragraph reveal until About section is almost visible.
            const paragraphProgress = clamp((progress - 0.22) / 0.46, 0, 1);
            // Keep list behavior close to current flow after paragraph reveal starts.
            const listProgress = clamp((progress - 0.36) / 0.56, 0, 1);

            applySequentialVisibility(aboutParagraphItems, paragraphProgress);
            applySequentialVisibility(aboutListItems, listProgress);
        };

        window.addEventListener("scroll", updateAboutSequence, { passive: true });
        window.addEventListener("resize", updateAboutSequence);
        updateAboutSequence();
    }

    const scrollSeqGroups = document.querySelectorAll("[data-scroll-seq]");
    if (scrollSeqGroups.length > 0) {
        const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
        let rafId = 0;

        const updateScrollSequenceGroups = () => {
            const viewportHeight = window.innerHeight || document.documentElement.clientHeight || 1;

            scrollSeqGroups.forEach((group) => {
                const items = Array.from(group.querySelectorAll(".scroll-seq-item"));
                if (!items.length) {
                    return;
                }

                const rect = group.getBoundingClientRect();
                const start = viewportHeight * 0.9;
                const end = -Math.max(rect.height * 0.18, viewportHeight * 0.12);
                const totalDistance = Math.max(1, start - end);
                const progress = clamp((start - rect.top) / totalDistance, 0, 1);
                const itemCount = items.length;

                items.forEach((item, index) => {
                    const threshold = (index + 1) / (itemCount + 1);
                    item.classList.toggle("is-visible", progress >= threshold);
                });
            });
        };

        const scheduleGroupUpdate = () => {
            if (rafId) {
                return;
            }
            rafId = window.requestAnimationFrame(() => {
                rafId = 0;
                updateScrollSequenceGroups();
            });
        };

        window.addEventListener("scroll", scheduleGroupUpdate, { passive: true });
        window.addEventListener("resize", scheduleGroupUpdate);
        updateScrollSequenceGroups();
    }

    const heroImageReveal = document.getElementById("heroImageReveal");
    const heroRevealLens = document.getElementById("heroRevealLens");
    if (heroImageReveal) {
        const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
        let lensSize = 140;
        let targetX = 0;
        let targetY = 0;
        let rafId = 0;
        let isActive = false;

        const updateLensSize = () => {
            const rect = heroImageReveal.getBoundingClientRect();
            lensSize = clamp(Math.round(Math.min(rect.width, rect.height) * 0.28), 104, 190);
            heroImageReveal.style.setProperty("--lens-size", `${lensSize}px`);
        };

        const setTarget = (clientX, clientY) => {
            const rect = heroImageReveal.getBoundingClientRect();
            targetX = clamp(clientX - rect.left, 0, rect.width);
            targetY = clamp(clientY - rect.top, 0, rect.height);
        };

        const renderReveal = () => {
            if (!isActive) {
                rafId = 0;
                return;
            }
            heroImageReveal.style.setProperty("--reveal-x", `${targetX}px`);
            heroImageReveal.style.setProperty("--reveal-y", `${targetY}px`);
            heroImageReveal.style.setProperty("--reveal-size", `${Math.round(lensSize * 0.5)}px`);
            rafId = window.requestAnimationFrame(renderReveal);
        };

        const startRevealLoop = () => {
            if (rafId) {
                return;
            }
            rafId = window.requestAnimationFrame(renderReveal);
        };

        const activateReveal = (clientX, clientY) => {
            setTarget(clientX, clientY);
            isActive = true;
            heroImageReveal.classList.add("is-active");
            if (heroRevealLens) {
                heroRevealLens.style.opacity = "1";
            }
            startRevealLoop();
        };

        const resetReveal = () => {
            isActive = false;
            if (rafId) {
                window.cancelAnimationFrame(rafId);
                rafId = 0;
            }
            heroImageReveal.style.setProperty("--reveal-size", "0px");
            heroImageReveal.classList.remove("is-active");
            if (heroRevealLens) {
                heroRevealLens.style.opacity = "0";
            }
        };

        const centerReveal = () => {
            const rect = heroImageReveal.getBoundingClientRect();
            heroImageReveal.style.setProperty("--reveal-x", `${rect.width / 2}px`);
            heroImageReveal.style.setProperty("--reveal-y", `${rect.height / 2}px`);
        };

        heroImageReveal.addEventListener("pointerenter", (event) => {
            activateReveal(event.clientX, event.clientY);
        });

        heroImageReveal.addEventListener("pointermove", (event) => {
            if (!isActive) {
                activateReveal(event.clientX, event.clientY);
                return;
            }
            setTarget(event.clientX, event.clientY);
        });

        heroImageReveal.addEventListener("pointerdown", (event) => {
            activateReveal(event.clientX, event.clientY);
        });

        heroImageReveal.addEventListener("pointerleave", resetReveal);
        heroImageReveal.addEventListener("pointercancel", resetReveal);
        heroImageReveal.addEventListener("pointerup", () => {
            if (window.matchMedia("(hover: none)").matches) {
                resetReveal();
            }
        });

        window.addEventListener("resize", () => {
            updateLensSize();
            if (!isActive) {
                centerReveal();
            }
        });
        updateLensSize();
        centerReveal();
        resetReveal();
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
                    // Scroll up: move tools strip to right (reverse direction)
                    offset += delta * scrollSpeedFactor;
                } else if (delta > 0) {
                    // Scroll down: also keep moving tools strip to left
                    offset += delta * scrollSpeedFactor;
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
