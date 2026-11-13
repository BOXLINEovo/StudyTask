/* StudyTask：自定义下拉面板 + 日期选择器 + 描述框自适应高度。
   原生 select / date input 仍保留在表单中负责提交，JS 只负责视觉与交互。 */
(function () {
  "use strict";

  function closeAll(except) {
    document.querySelectorAll(".select-wrap.open").forEach(function (wrap) {
      if (wrap !== except) {
        wrap.classList.remove("open");
        var trigger = wrap.querySelector(".select-trigger");
        if (trigger) trigger.setAttribute("aria-expanded", "false");
      }
    });
  }

  function closeAllDates(except) {
    document.querySelectorAll(".date-wrap.open").forEach(function (wrap) {
      if (wrap !== except) {
        wrap.classList.remove("open");
        var trigger = wrap.querySelector(".date-trigger");
        if (trigger) trigger.setAttribute("aria-expanded", "false");
      }
    });
  }

  function positionPanel(panel, trigger) {
    var rect = trigger.getBoundingClientRect();
    panel.style.position = "fixed";
    panel.style.left = rect.left + "px";
    panel.style.right = "auto";
    panel.style.width = rect.width + "px";
    panel.style.top = rect.bottom + 6 + "px";
    panel.style.bottom = "auto";

    var panelRect = panel.getBoundingClientRect();
    if (rect.bottom + panelRect.height + 8 > window.innerHeight && rect.top - panelRect.height - 6 > 8) {
      panel.style.top = rect.top - panelRect.height - 6 + "px";
    }
  }

  function positionDatePanel(panel, trigger) {
    var rect = trigger.getBoundingClientRect();
    var width = 300;
    var left = rect.left;
    if (left + width > window.innerWidth - 12) left = window.innerWidth - width - 12;
    if (left < 12) left = 12;

    panel.style.position = "fixed";
    panel.style.left = left + "px";
    panel.style.right = "auto";
    panel.style.width = width + "px";
    panel.style.top = rect.bottom + 6 + "px";
    panel.style.bottom = "auto";

    var panelRect = panel.getBoundingClientRect();
    if (rect.bottom + panelRect.height + 8 > window.innerHeight && rect.top - panelRect.height - 6 > 8) {
      panel.style.top = rect.top - panelRect.height - 6 + "px";
    }
  }

  function enhance(select) {
    if (select.dataset.enhanced === "1") return;
    select.dataset.enhanced = "1";

    var wrap = document.createElement("div");
    wrap.className = "select-wrap";
    select.parentNode.insertBefore(wrap, select);
    wrap.appendChild(select);
    select.classList.add("native-select");
    select.setAttribute("tabindex", "-1");

    var trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "select-trigger";
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");
    trigger.textContent = select.options[select.selectedIndex]
      ? select.options[select.selectedIndex].text
      : "";
    wrap.appendChild(trigger);

    var panel = document.createElement("div");
    panel.className = "select-menu";
    panel.setAttribute("role", "listbox");
    wrap.appendChild(panel);

    function syncTrigger() {
      trigger.textContent = select.options[select.selectedIndex]
        ? select.options[select.selectedIndex].text
        : "";
    }

    function build() {
      panel.innerHTML = "";
      Array.prototype.forEach.call(select.options, function (opt) {
        var item = document.createElement("div");
        item.className = "select-option";
        item.setAttribute("role", "option");
        item.dataset.value = opt.value;
        item.textContent = opt.text;
        if (opt.selected) item.setAttribute("aria-selected", "true");
        item.addEventListener("click", function (event) {
          event.preventDefault();
          event.stopPropagation();
          select.value = opt.value;
          select.dispatchEvent(new Event("change", { bubbles: true }));
          syncTrigger();
          wrap.classList.remove("open");
          trigger.setAttribute("aria-expanded", "false");
          trigger.focus();
        });
        panel.appendChild(item);
      });
    }

    trigger.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      var isOpen = wrap.classList.contains("open");
      closeAll(wrap);
      closeAllDates(null);
      if (isOpen) {
        wrap.classList.remove("open");
        trigger.setAttribute("aria-expanded", "false");
        return;
      }
      wrap.classList.add("open");
      trigger.setAttribute("aria-expanded", "true");
      build();
      positionPanel(panel, trigger);
    });

    trigger.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        wrap.classList.remove("open");
        trigger.setAttribute("aria-expanded", "false");
        return;
      }
      if (event.key === "ArrowDown" || event.key === "ArrowUp") {
        event.preventDefault();
        if (!wrap.classList.contains("open")) {
          trigger.click();
          return;
        }
        var options = Array.prototype.slice.call(panel.querySelectorAll(".select-option"));
        var index = options.findIndex(function (o) {
          return o.getAttribute("aria-selected") === "true";
        });
        index = event.key === "ArrowDown"
          ? Math.min(options.length - 1, index + 1)
          : Math.max(0, index - 1);
        options.forEach(function (o) { o.classList.remove("active"); });
        if (options[index]) {
          options[index].classList.add("active");
          options[index].scrollIntoView({ block: "nearest" });
        }
        return;
      }
      if (event.key === "Enter" && wrap.classList.contains("open")) {
        event.preventDefault();
        var active = panel.querySelector(".select-option.active");
        if (active) active.click();
      }
    });

    panel.addEventListener("click", function (event) {
      event.stopPropagation();
    });

    select.addEventListener("change", syncTrigger);
  }

  function pad(n) { return String(n).padStart(2, "0"); }
  function fmtDate(d) {
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  }
  function parseDate(value) {
    if (!value) return null;
    var parts = value.split("-").map(Number);
    if (parts.length !== 3 || !parts[0] || !parts[1] || !parts[2]) return null;
    var d = new Date(parts[0], parts[1] - 1, parts[2]);
    return isNaN(d.getTime()) ? null : d;
  }

  function enhanceDate(input) {
    if (input.dataset.dateEnhanced === "1") return;
    input.dataset.dateEnhanced = "1";

    var wrap = document.createElement("div");
    wrap.className = "date-wrap";
    input.parentNode.insertBefore(wrap, input);
    wrap.appendChild(input);
    input.classList.add("native-date");
    input.setAttribute("tabindex", "-1");

    var trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "date-trigger";
    trigger.setAttribute("aria-haspopup", "dialog");
    trigger.setAttribute("aria-expanded", "false");
    wrap.appendChild(trigger);

    var panel = document.createElement("div");
    panel.className = "date-menu";
    panel.setAttribute("role", "dialog");
    wrap.appendChild(panel);

    var viewYear = new Date().getFullYear();
    var viewMonth = new Date().getMonth();

    function updateTrigger() {
      var selected = parseDate(input.value);
      trigger.textContent = selected ? fmtDate(selected) : "请选择日期";
      trigger.classList.toggle("placeholder", !selected);
    }

    function render() {
      var today = new Date();
      today.setHours(0, 0, 0, 0);
      var selected = parseDate(input.value);
      var first = new Date(viewYear, viewMonth, 1);
      var start = first.getDay();
      var days = new Date(viewYear, viewMonth + 1, 0).getDate();

      var html = "";
      html += '<div class="date-head">';
      html += '<button type="button" class="date-nav" data-nav="-1" aria-label="上个月">‹</button>';
      html += '<span class="date-title">' + viewYear + "年" + (viewMonth + 1) + "月</span>";
      html += '<button type="button" class="date-nav" data-nav="1" aria-label="下个月">›</button>';
      html += "</div>";
      html += '<div class="date-week"><span>日</span><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span></div>';
      html += '<div class="date-grid">';
      for (var i = 0; i < start; i++) {
        html += '<span class="date-cell muted"></span>';
      }
      for (var day = 1; day <= days; day++) {
        var d = new Date(viewYear, viewMonth, day);
        var cls = "date-cell";
        if (selected && d.getFullYear() === selected.getFullYear() &&
            d.getMonth() === selected.getMonth() && d.getDate() === selected.getDate()) {
          cls += " selected";
        } else if (d.getTime() === today.getTime()) {
          cls += " today";
        }
        html += '<button type="button" class="' + cls + '" data-day="' + day + '">' + day + "</button>";
      }
      html += "</div>";
      html += '<div class="date-foot">';
      html += '<button type="button" class="date-action" data-action="cancel">取消</button>';
      html += '<button type="button" class="date-action primary" data-action="today">今天</button>';
      html += "</div>";
      panel.innerHTML = html;
    }

    function open() {
      var selected = parseDate(input.value) || new Date();
      viewYear = selected.getFullYear();
      viewMonth = selected.getMonth();
      render();
      wrap.classList.add("open");
      trigger.setAttribute("aria-expanded", "true");
      positionDatePanel(panel, trigger);
    }

    function close() {
      wrap.classList.remove("open");
      trigger.setAttribute("aria-expanded", "false");
    }

    function applyDate(d) {
      input.value = fmtDate(d);
      input.dispatchEvent(new Event("change", { bubbles: true }));
      updateTrigger();
      close();
      trigger.focus();
    }

    trigger.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      var isOpen = wrap.classList.contains("open");
      closeAll(null);
      closeAllDates(wrap);
      if (isOpen) {
        close();
        return;
      }
      open();
    });

    panel.addEventListener("click", function (event) {
      event.stopPropagation();
      var nav = event.target.closest("[data-nav]");
      if (nav) {
        viewMonth += Number(nav.dataset.nav);
        if (viewMonth < 0) { viewMonth = 11; viewYear -= 1; }
        if (viewMonth > 11) { viewMonth = 0; viewYear += 1; }
        render();
        positionDatePanel(panel, trigger);
        return;
      }
      var dayBtn = event.target.closest("[data-day]");
      if (dayBtn) {
        applyDate(new Date(viewYear, viewMonth, Number(dayBtn.dataset.day)));
        return;
      }
      var action = event.target.closest("[data-action]");
      if (action) {
        if (action.dataset.action === "today") {
          applyDate(new Date());
        } else {
          close();
          trigger.focus();
        }
      }
    });

    input.addEventListener("change", updateTrigger);
    trigger.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        close();
      }
    });

    updateTrigger();
  }

  document.querySelectorAll("select").forEach(enhance);
  document.querySelectorAll('input[type="date"]').forEach(enhanceDate);

  /* 点击标签文字也能打开自定义面板，避免触发隐藏的原生控件 */
  document.querySelectorAll("label").forEach(function (label) {
    var hasSelect = !!label.querySelector(".select-wrap");
    var hasDate = !!label.querySelector(".date-wrap");
    if (!hasSelect && !hasDate) return;
    label.addEventListener("click", function (event) {
      if (event.target.closest(".select-trigger, .select-menu, .date-trigger, .date-menu")) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      var trigger = hasSelect
        ? label.querySelector(".select-trigger")
        : label.querySelector(".date-trigger");
      if (trigger) trigger.click();
    });
  });

  /* 任务描述框：限制最大高度，内容增加时自动增高，超过后滚动 */
  document.querySelectorAll("textarea.auto-grow").forEach(function (textarea) {
    var maxHeight = 260;
    function resize() {
      textarea.style.height = "auto";
      var next = Math.min(textarea.scrollHeight, maxHeight);
      textarea.style.height = next + "px";
      textarea.style.overflowY = textarea.scrollHeight > maxHeight ? "auto" : "hidden";
    }
    textarea.addEventListener("input", resize);
    window.addEventListener("resize", resize);
    resize();
  });

  document.addEventListener("click", function () {
    closeAll(null);
    closeAllDates(null);
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      closeAll(null);
      closeAllDates(null);
    }
  });
  window.addEventListener("resize", function () {
    closeAll(null);
    closeAllDates(null);
  });
  window.addEventListener("scroll", function () {
    closeAll(null);
    closeAllDates(null);
  }, true);
})();
