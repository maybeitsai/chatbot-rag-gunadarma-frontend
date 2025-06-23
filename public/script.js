/**
 * Custom Chainlit Watermark Replacer
 * Mengganti "Built with Chainlit" menjadi "© 2025 Harry Mardika"
 * Author: Harry Mardika
 * Year: 2025
 */

(function () {
  "use strict";

  let isWatermarkCustomized = false;
  let observerInstance = null;

  /**
   * Fungsi utama untuk mengubah watermark
   */
  function customizeWatermark() {
    // Jika sudah dikustomisasi, skip
    if (isWatermarkCustomized) return;

    // Cari elemen watermark dengan berbagai selector
    const watermarkSelectors = [
      "a.watermark",
      'a[href*="chainlit.io"]',
      ".watermark",
      '[class*="watermark"]',
    ];

    let watermarkElement = null;

    for (const selector of watermarkSelectors) {
      watermarkElement = document.querySelector(selector);
      if (watermarkElement) break;
    }

    // Jika tidak ditemukan, coba cari berdasarkan teks
    if (!watermarkElement) {
      const elements = document.querySelectorAll("a, div, span");
      for (const el of elements) {
        if (
          el.textContent &&
          el.textContent.toLowerCase().includes("built with")
        ) {
          watermarkElement = el.closest("a") || el;
          break;
        }
      }
    }

    if (watermarkElement) {
      try {
        // Hapus atribut link jika ada
        watermarkElement.removeAttribute("href");
        watermarkElement.removeAttribute("target");

        // Tambah atau update class watermark
        watermarkElement.classList.add("watermark");

        // Ganti konten dengan copyright
        watermarkElement.innerHTML = `
                    <div class="text-xs text-muted-foreground">
                        <span>Copyright © 2025 Harry Mardika</span>
                    </div>
                `;

        // Ubah styling untuk menghilangkan behavior link
        watermarkElement.style.cursor = "default";
        watermarkElement.style.textDecoration = "none";
        watermarkElement.style.pointerEvents = "none";

        // Tandai bahwa watermark sudah dikustomisasi
        watermarkElement.setAttribute("data-customized", "true");
        isWatermarkCustomized = true;

        console.log('✅ Watermark berhasil diubah ke "© 2025 Harry Mardika"');

        // Hentikan observer karena sudah berhasil
        if (observerInstance) {
          observerInstance.disconnect();
          observerInstance = null;
        }
      } catch (error) {
        console.error("❌ Error saat mengubah watermark:", error);
      }
    }
  }

  /**
   * Observer untuk memantau perubahan DOM
   */
  function setupWatermarkObserver() {
    if (observerInstance) return; // Jangan buat observer ganda

    observerInstance = new MutationObserver(function (mutations) {
      // Jika sudah dikustomisasi, hentikan observer
      if (isWatermarkCustomized) {
        observerInstance.disconnect();
        return;
      }

      let shouldCheck = false;

      mutations.forEach(function (mutation) {
        if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
          // Cek apakah ada node baru yang ditambahkan
          for (const node of mutation.addedNodes) {
            if (node.nodeType === 1) {
              // Element node
              shouldCheck = true;
              break;
            }
          }
        }
      });

      if (shouldCheck) {
        setTimeout(customizeWatermark, 50);
      }
    });

    // Mulai observasi pada body dengan konfigurasi yang optimal
    if (document.body) {
      observerInstance.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: false,
        characterData: false,
      });
    }
  }

  /**
   * Fungsi inisialisasi utama
   */
  function initialize() {
    console.log("🔄 Menginisialisasi custom watermark...");

    // Reset flag jika halaman baru
    isWatermarkCustomized = false;

    // Coba customisasi langsung
    customizeWatermark();

    // Jika belum berhasil, setup observer
    if (!isWatermarkCustomized) {
      setupWatermarkObserver();

      // Coba lagi setelah delay yang berbeda
      const delays = [100, 250, 500, 1000, 2000];
      delays.forEach((delay) => {
        setTimeout(() => {
          if (!isWatermarkCustomized) {
            customizeWatermark();
          }
        }, delay);
      });
    }
  }

  /**
   * Event listeners untuk berbagai state halaman
   */

  // Jika DOM sudah ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    // DOM sudah ready, jalankan langsung
    initialize();
  }

  // Backup untuk window load
  window.addEventListener("load", function () {
    setTimeout(function () {
      if (!isWatermarkCustomized) {
        initialize();
      }
    }, 100);
  });

  // Handle navigasi SPA (Single Page Application)
  let currentUrl = window.location.href;
  new MutationObserver(function () {
    if (window.location.href !== currentUrl) {
      currentUrl = window.location.href;
      isWatermarkCustomized = false;
      setTimeout(initialize, 200);
    }
  }).observe(document.body, { childList: true, subtree: true });
})();
