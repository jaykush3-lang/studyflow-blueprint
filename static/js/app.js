document.addEventListener("DOMContentLoaded", () => {
  const cursorOrb = document.querySelector(".cursor-orb");
  const cursorRing = document.querySelector(".cursor-ring");
  const quoteText = document.querySelector("[data-quote-text]");
  const quoteAuthor = document.querySelector("[data-quote-author]");
  const quoteItems = Array.from(document.querySelectorAll("[data-quote-item]"));
  const liveTime = document.querySelector("[data-live-time]");
  const liveDate = document.querySelector("[data-live-date]");
  const calendarTitle = document.querySelector("[data-calendar-title]");
  const calendarSubtitle = document.querySelector("[data-calendar-subtitle]");
  const calendarGrid = document.querySelector("[data-calendar-grid]");

  if (
    cursorOrb &&
    cursorRing &&
    window.matchMedia("(hover: hover) and (pointer: fine)").matches
  ) {
    let pointerX = window.innerWidth / 2;
    let pointerY = window.innerHeight / 2;
    let orbX = pointerX;
    let orbY = pointerY;
    let ringX = pointerX;
    let ringY = pointerY;

    const setHoverState = (active, magneticTarget) => {
      cursorOrb.classList.toggle("cursor-hover", active);
      cursorRing.classList.toggle("cursor-hover", active);
      cursorRing.classList.toggle("cursor-magnetic", Boolean(magneticTarget));
    };

    const updatePointer = (x, y) => {
      pointerX = x;
      pointerY = y;
      cursorOrb.classList.add("cursor-visible");
      cursorRing.classList.add("cursor-visible");
    };

    document.addEventListener("mousemove", (event) => {
      updatePointer(event.clientX, event.clientY);
    });

    document.addEventListener("mouseleave", () => {
      cursorOrb.classList.remove("cursor-visible");
      cursorRing.classList.remove("cursor-visible");
    });

    document.querySelectorAll("a, button, input, textarea, select, .track-card, .goal-card, .item-card, .panel, .hero").forEach((element) => {
      element.addEventListener("mouseenter", () => {
        setHoverState(true, true);
      });
      element.addEventListener("mouseleave", () => {
        setHoverState(false, false);
      });
    });

    const animateCursor = () => {
      orbX += (pointerX - orbX) * 0.22;
      orbY += (pointerY - orbY) * 0.22;
      ringX += (pointerX - ringX) * 0.12;
      ringY += (pointerY - ringY) * 0.12;

      cursorOrb.style.transform = `translate(${orbX}px, ${orbY}px) translate(-50%, -50%)`;
      cursorRing.style.transform = `translate(${ringX}px, ${ringY}px) translate(-50%, -50%)`;

      window.requestAnimationFrame(animateCursor);
    };

    window.requestAnimationFrame(animateCursor);
  }

  if (quoteText && quoteAuthor && quoteItems.length > 0) {
    let currentIndex = quoteItems.findIndex((item) => item.dataset.active === "true");
    if (currentIndex < 0) currentIndex = 0;

    const applyQuote = (index) => {
      const item = quoteItems[index];
      quoteText.textContent = `"${item.dataset.quote}"`;
      quoteAuthor.textContent = item.dataset.author;
      quoteItems.forEach((quoteItem, quoteIndex) => {
        quoteItem.dataset.active = quoteIndex === index ? "true" : "false";
      });
    };

    setInterval(() => {
      currentIndex = (currentIndex + 1) % quoteItems.length;
      applyQuote(currentIndex);
    }, 4500);
  }

  if (liveTime && liveDate) {
    const updateClock = () => {
      const now = new Date();
      liveTime.textContent = now.toLocaleTimeString();
      liveDate.textContent = now.toLocaleDateString(undefined, {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    };

    updateClock();
    setInterval(updateClock, 1000);
  }

  if (calendarTitle && calendarGrid) {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDate = new Date(year, month + 1, 0).getDate();
    const startOffset = firstDay.getDay();
    const weekdayLabels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    calendarTitle.textContent = now.toLocaleDateString(undefined, {
      month: "long",
      year: "numeric",
    });
    if (calendarSubtitle) {
      calendarSubtitle.textContent = `Today is ${now.toLocaleDateString(undefined, {
        day: "numeric",
        month: "short",
        year: "numeric",
      })}`;
    }

    weekdayLabels.forEach((label) => {
      const cell = document.createElement("div");
      cell.className = "calendar-label";
      cell.textContent = label;
      calendarGrid.appendChild(cell);
    });

    for (let i = 0; i < startOffset; i += 1) {
      const blank = document.createElement("div");
      blank.className = "calendar-cell calendar-cell-empty";
      calendarGrid.appendChild(blank);
    }

    for (let day = 1; day <= lastDate; day += 1) {
      const cell = document.createElement("div");
      cell.className = "calendar-cell";
      if (day === now.getDate()) {
        cell.classList.add("calendar-cell-today");
      }
      cell.textContent = String(day);
      calendarGrid.appendChild(cell);
    }
  }
});
