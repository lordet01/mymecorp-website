(function (global) {
    "use strict";

    var SUPPORTED = { en: true, ko: true, ja: true, et: true };

    function normalize(lang) {
        lang = String(lang || "en").toLowerCase();
        return SUPPORTED[lang] ? lang : "en";
    }

    function getStoredLanguage() {
        try {
            var stored = (localStorage.getItem("myme_lang") || "").toLowerCase();
            if (SUPPORTED[stored]) return stored;
        } catch (e) {}
        return null;
    }

    function setStoredLanguage(lang) {
        try {
            localStorage.setItem("myme_lang", normalize(lang));
        } catch (e) {}
    }

    function getForcedLanguage() {
        try {
            var params = new URLSearchParams(window.location.search);
            var lang = (params.get("lang") || "").toLowerCase();
            if (SUPPORTED[lang]) return lang;
        } catch (e) {}
        return null;
    }

    function getBrowserLanguage() {
        var browserLang = (navigator.language || "").toLowerCase();
        if (browserLang.indexOf("ko") === 0) return "ko";
        if (browserLang.indexOf("ja") === 0) return "ja";
        if (browserLang.indexOf("et") === 0) return "et";
        return "en";
    }

    function fetchCountryCodeWithTimeout() {
        var timeout = new Promise(function (resolve) {
            setTimeout(function () { resolve(null); }, 1800);
        });
        var request = fetch("https://ipapi.co/json/", { cache: "no-store" })
            .then(function (res) { return res.ok ? res.json() : null; })
            .then(function (data) {
                if (!data || !data.country_code) return null;
                return String(data.country_code).toUpperCase();
            })
            .catch(function () { return null; });
        return Promise.race([request, timeout]);
    }

    function applyLanguage(copy, lang) {
        var normalized = normalize(lang);
        var dict = copy[normalized] || copy.en || {};
        var i;

        document.documentElement.setAttribute("lang", normalized);

        var selector = document.getElementById("lang-select");
        if (selector) selector.value = normalized;

        var nodes = document.querySelectorAll("[data-i18n-key]");
        for (i = 0; i < nodes.length; i += 1) {
            var key = nodes[i].getAttribute("data-i18n-key");
            if (dict[key] != null) nodes[i].innerHTML = dict[key];
        }

        var ariaNodes = document.querySelectorAll("[data-i18n-aria-key]");
        for (i = 0; i < ariaNodes.length; i += 1) {
            var ariaKey = ariaNodes[i].getAttribute("data-i18n-aria-key");
            if (dict[ariaKey] != null) ariaNodes[i].setAttribute("aria-label", dict[ariaKey]);
        }

        var altNodes = document.querySelectorAll("[data-i18n-alt-key]");
        for (i = 0; i < altNodes.length; i += 1) {
            var altKey = altNodes[i].getAttribute("data-i18n-alt-key");
            if (dict[altKey] != null) altNodes[i].setAttribute("alt", dict[altKey]);
        }

        var titleKey = document.querySelector("title[data-i18n-key]");
        if (titleKey) {
            var tKey = titleKey.getAttribute("data-i18n-key");
            if (dict[tKey]) document.title = dict[tKey].replace(/<[^>]+>/g, "");
        }

        var metaDesc = document.querySelector('meta[name="description"][data-i18n-key]');
        if (metaDesc) {
            var dKey = metaDesc.getAttribute("data-i18n-key");
            if (dict[dKey]) metaDesc.setAttribute("content", dict[dKey]);
        }
    }

    function init(copy) {
        function setLang(lang) {
            var next = normalize(lang);
            setStoredLanguage(next);
            applyLanguage(copy, next);
        }

        var selector = document.getElementById("lang-select");
        if (selector) {
            selector.addEventListener("change", function (event) {
                setLang(event.target.value);
            });
        }

        var forced = getForcedLanguage();
        if (forced) {
            applyLanguage(copy, forced);
            return;
        }

        var stored = getStoredLanguage();
        if (stored) {
            applyLanguage(copy, stored);
            return;
        }

        fetchCountryCodeWithTimeout()
            .then(function (countryCode) {
                if (countryCode === "KR") return applyLanguage(copy, "ko");
                if (countryCode === "JP") return applyLanguage(copy, "ja");
                if (countryCode === "EE") return applyLanguage(copy, "et");
                if (countryCode) return applyLanguage(copy, "en");
                applyLanguage(copy, getBrowserLanguage());
            })
            .catch(function () {
                applyLanguage(copy, getBrowserLanguage());
            });
    }

    global.MymeI18n = {
        init: init,
        applyLanguage: applyLanguage,
        normalize: normalize
    };
})(window);
