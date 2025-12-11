let map;
let marker;
let csrfToken = null;

// Obtener CSRF token al cargar la página
fetch('/csrf-token')
    .then(r => r.json())
    .then(data => {
        csrfToken = data.csrf_token;
        console.log('✅ CSRF token obtenido');
    })
    .catch(err => {
        console.warn('⚠️ No se pudo obtener CSRF token (protección desactivada):', err);
    });

// Función auxiliar para establecer contenido de forma segura
function safeSetTextContent(elementId, content) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = content;
    } else {
        console.warn(`Element with ID '${elementId}' not found`);
    }
}

// Función auxiliar para establecer clase de forma segura
function safeSetClassName(elementId, className) {
    const element = document.getElementById(elementId);
    if (element) {
        element.className = className;
    } else {
        console.warn(`Element with ID '${elementId}' not found`);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar iconos Lucide
    lucide.createIcons();
    
    const ipInput = document.getElementById('ipInput');
    const verifyBtn = document.getElementById('verifyBtn');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const topBar = document.getElementById('topBar');

    // Control de la barra superior con scroll
    let lastScrollTop = 0;
    const scrollThreshold = 100;

    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > scrollThreshold) {
            topBar.classList.remove('hidden');
            topBar.classList.add('visible');
        } else {
            topBar.classList.add('hidden');
            topBar.classList.remove('visible');
        }
        
        lastScrollTop = scrollTop;
    });

    // Event listeners
    verifyBtn.addEventListener('click', verifyIP);
    ipInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            verifyIP();
        }
    });


    async function verifyIP() {
        const ip = ipInput.value.trim();
        
        if (!ip) {
            alert('Por favor ingresa una dirección IP');
            return;
        }

        // Show loading
        loading.classList.remove('hidden');
        results.classList.add('hidden');
        verifyBtn.disabled = true;
        verifyBtn.innerHTML = '<i data-lucide="loader-2"></i> Verificando...';
        lucide.createIcons();

        try {
            // Preparar headers con CSRF token si está disponible
            const headers = {
                'Content-Type': 'application/json',
            };
            
            if (csrfToken) {
                headers['X-CSRFToken'] = csrfToken;
            }
            
            const response = await fetch('/verify', {
                method: 'POST',
                headers: headers,
                body: JSON.stringify({ ip: ip })
            });

            const data = await response.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            displayResults(data);
        } catch (error) {
            console.error('Error detallado:', error);
            alert('Error al verificar la IP: ' + error.message);
        } finally {
            loading.classList.add('hidden');
            verifyBtn.disabled = false;
            verifyBtn.innerHTML = '<i data-lucide="search"></i> Verificar';
            lucide.createIcons();
        }
    }

    function displayResults(data) {
        console.log('Datos recibidos:', data);
        
        // 1. Actualizar resumen con datos de AbuseIPDB
        safeSetTextContent('verifiedIP', data.ip);
        
        if (data.abuseipdb) {
            const confidence = data.abuseipdb.abuse_confidence || 0;
            const reports = data.abuseipdb.total_reports || 0;
            const isWhitelisted = data.abuseipdb.is_whitelisted;
            
            // Calcular confianza actual (inversa al abuso)
            let currentTrust = 100;
            let trustClass = 'security-safe';
            
            if (isWhitelisted) {
                currentTrust = 100;
                trustClass = 'security-verified';
            } else if (confidence === 0 && reports === 0) {
                currentTrust = 100;
                trustClass = 'security-safe';
            } else if (confidence === 0 && reports <= 5) {
                currentTrust = 95;
                trustClass = 'security-safe';
            } else if (confidence === 0 && reports <= 50) {
                currentTrust = 85;
                trustClass = 'security-caution';
            } else if (confidence === 0 && reports > 50) {
                currentTrust = 70;
                trustClass = 'security-moderate';
            } else if (confidence > 0 && confidence <= 25) {
                currentTrust = Math.max(50, 100 - confidence - Math.min(reports / 10, 25));
                trustClass = 'security-moderate';
            } else if (confidence > 25 && confidence <= 50) {
                currentTrust = Math.max(25, 75 - confidence);
                trustClass = 'security-suspicious';
            } else if (confidence > 50 && confidence <= 75) {
                currentTrust = Math.max(15, 50 - confidence / 2);
                trustClass = 'security-suspicious';
            } else {
                currentTrust = Math.max(5, 25 - confidence / 4);
                trustClass = 'security-dangerous';
            }
            
            currentTrust = Math.round(currentTrust);
            safeSetTextContent('summaryAbuseConfidence', `${currentTrust}%`);
            safeSetTextContent('summaryTotalReports', reports.toLocaleString());
            
            // Estado de seguridad
            let securityStatus = 'Segura';
            let securityClass = 'security-safe';
            
            if (isWhitelisted) {
                securityStatus = 'Verificada';
                securityClass = 'security-verified';
            } else if (confidence > 75) {
                securityStatus = 'Peligrosa';
                securityClass = 'security-dangerous';
            } else if (confidence > 50) {
                securityStatus = 'Sospechosa';
                securityClass = 'security-suspicious';
            } else if (confidence > 25) {
                securityStatus = 'Moderada';
                securityClass = 'security-moderate';
            } else if (reports > 100) {
                securityStatus = 'Histórico Alto';
                securityClass = 'security-caution';
            } else if (reports > 10) {
                securityStatus = 'Histórico Bajo';
                securityClass = 'security-caution';
            } else if (reports > 0) {
                securityStatus = 'Precaución';
                securityClass = 'security-caution';
            }
            
            const securityElement = document.getElementById('summarySecurityStatus');
            if (securityElement) {
                securityElement.textContent = securityStatus;
                securityElement.className = `value ${securityClass}`;
            }
            
            // Actualizar colores
            const reportsElement = document.getElementById('summaryTotalReports');
            if (reportsElement) {
                if (reports === 0) {
                    reportsElement.className = 'value security-safe';
                } else if (reports <= 10) {
                    reportsElement.className = 'value security-caution';
                } else if (reports <= 100) {
                    reportsElement.className = 'value security-moderate';
                } else {
                    reportsElement.className = 'value red';
                }
            }
            
            const confidenceElement = document.getElementById('summaryAbuseConfidence');
            if (confidenceElement) {
                confidenceElement.className = `value ${trustClass}`;
            }
        } else {
            safeSetTextContent('summaryAbuseConfidence', 'N/A');
            safeSetTextContent('summaryTotalReports', 'N/A');
            safeSetTextContent('summarySecurityStatus', 'Sin datos');
        }

        // 2. Actualizar evaluación de confianza
        updateTrustAssessment(data.abuseipdb);

        // 3. Actualizar geolocalización
        updateGeolocation(data.geolocation);

        // 4. Actualizar lista de fuentes donde se verifica/lista la IP
        updateSourcesList(data);        // 5. Mostrar resultados
        results.classList.remove('hidden');
    }

    function updateSourcesList(data) {
        // Actualizar resumen de blacklists
        updateBlacklistSummary(data);
        
        // Llenar lista detallada (oculta por defecto)
        updateBlacklistDetails(data);
        
        // Manejar toggle de detalles
        setupToggleDetails();
    }

    function updateBlacklistSummary(data) {
        let totalChecked = 0;
        let totalListed = 0;

        // AbuseIPDB
        if (data.abuseipdb) {
            totalChecked += 1;
            const confidence = data.abuseipdb.abuse_confidence || 0;
            const reports = data.abuseipdb.total_reports || 0;
            if (!data.abuseipdb.is_whitelisted && (confidence > 0 || reports > 0)) {
                totalListed += 1;
            }
        }

        // Blacklists DNS
        if (data.dns_blacklists) {
            for (const [host, info] of Object.entries(data.dns_blacklists)) {
                totalChecked += 1;
                if (info.listed) {
                    totalListed += 1;
                }
            }
        }

        const percentage = totalChecked > 0 ? Math.round((totalListed / totalChecked) * 100) : 0;

        safeSetTextContent('totalChecked', totalChecked.toString());
        safeSetTextContent('totalListed', totalListed.toString());
        safeSetTextContent('blacklistPercentage', `${percentage}%`);
    }

    function updateBlacklistDetails(data) {
        const container = document.getElementById('blacklistDetailsList');
        if (!container) return;

        // Limpiar contenido previo
        container.innerHTML = '';

        const sources = [];

        // AbuseIPDB (principal fuente de reputación)
        if (data.abuseipdb) {
            const a = data.abuseipdb;
            const confidence = a.abuse_confidence || 0;
            const reports = a.total_reports || 0;
            const isWhitelisted = a.is_whitelisted;
            const listed = isWhitelisted ? false : (confidence > 0 || reports > 0);
            sources.push({
                name: 'AbuseIPDB',
                listed: listed,
                detail: isWhitelisted ? 'IP en lista blanca' : `${confidence}% confianza de abuso, ${reports} reportes`,
                hint: a.api_used ? 'Datos vía API' : 'Datos simulados',
                category: 'primary'
            });
        }

        // Blacklists DNS individuales (NUEVAS - datos reales)
        if (data.dns_blacklists) {
            // Agrupar por tipo para mejor organización
            const spamhausLists = [];
            const surblLists = [];
            const sorbsLists = [];
            const otherLists = [];

            for (const [host, info] of Object.entries(data.dns_blacklists)) {
                const listInfo = {
                    name: info.name || host,
                    listed: info.listed || false,
                    detail: info.listed ? 'IP listada' : 'IP no listada',
                    hint: info.error ? `Error: ${info.error}` : 'DNS consultado',
                    category: 'blacklist'
                };

                if (host.includes('spamhaus')) {
                    spamhausLists.push(listInfo);
                } else if (host.includes('surbl') || host.includes('uribl')) {
                    surblLists.push(listInfo);
                } else if (host.includes('sorbs')) {
                    sorbsLists.push(listInfo);
                } else {
                    otherLists.push(listInfo);
                }
            }

            // Agregar separadores y listas organizadas
            if (spamhausLists.length > 0) {
                sources.push({
                    name: '--- Spamhaus ---',
                    listed: false,
                    detail: '',
                    hint: '',
                    category: 'separator'
                });
                sources.push(...spamhausLists);
            }

            if (surblLists.length > 0) {
                sources.push({
                    name: '--- SURBL/URIBL ---',
                    listed: false,
                    detail: '',
                    hint: '',
                    category: 'separator'
                });
                sources.push(...surblLists);
            }

            if (sorbsLists.length > 0) {
                sources.push({
                    name: '--- SORBS ---',
                    listed: false,
                    detail: '',
                    hint: '',
                    category: 'separator'
                });
                sources.push(...sorbsLists);
            }

            if (otherLists.length > 0) {
                sources.push({
                    name: '--- Otras Blacklists ---',
                    listed: false,
                    detail: '',
                    hint: '',
                    category: 'separator'
                });
                sources.push(...otherLists);
            }
        }

        // Renderizar cada fuente
        sources.forEach(src => {
            const item = document.createElement('div');
            
            // Aplicar clases CSS según el tipo
            if (src.category === 'separator') {
                item.className = 'source-separator';
                item.textContent = src.name;
                container.appendChild(item);
                return;
            } else if (src.category === 'primary') {
                item.className = 'source-item source-primary';
            } else if (src.category === 'summary') {
                item.className = 'source-item source-summary';
            } else if (src.category === 'blacklist') {
                item.className = 'source-item source-blacklist';
            } else {
                item.className = 'source-item';
            }

            const name = document.createElement('div');
            name.className = 'source-name';
            name.textContent = src.name;

            const status = document.createElement('div');
            status.className = `source-status ${src.listed ? 'listed' : 'not-listed'}`;
            status.textContent = src.listed ? 'Listado' : 'No listado';

            const detail = document.createElement('div');
            detail.className = 'source-detail';
            detail.textContent = src.detail || '';

            if (src.hint) {
                const hint = document.createElement('div');
                hint.className = 'source-hint';
                hint.textContent = src.hint;
                item.appendChild(hint);
            }

            item.appendChild(name);
            item.appendChild(status);
            item.appendChild(detail);

            container.appendChild(item);
        });
    }

    function setupToggleDetails() {
        const toggleBtn = document.getElementById('toggleDetails');
        const detailsContent = document.getElementById('blacklistDetailsList');
        
        if (!toggleBtn || !detailsContent) return;

        toggleBtn.addEventListener('click', function() {
            const isHidden = detailsContent.classList.contains('hidden');
            
            if (isHidden) {
                detailsContent.classList.remove('hidden');
                toggleBtn.classList.add('expanded');
                toggleBtn.querySelector('span').textContent = 'Ocultar detalles por blacklist';
            } else {
                detailsContent.classList.add('hidden');
                toggleBtn.classList.remove('expanded');
                toggleBtn.querySelector('span').textContent = 'Ver detalles por blacklist';
            }
        });

        // Recrear iconos Lucide
        try { lucide.createIcons(); } catch (e) { /* ignore */ }
    }

    function updateTrustAssessment(abuseipdb) {
        const trustCircle = document.querySelector('.trust-circle');
        const trustPercentage = document.getElementById('trustPercentage');
        const trustStatus = document.getElementById('trustStatus');
        const trustDescription = document.getElementById('trustDescription');

        if (!abuseipdb) {
            if (trustCircle) trustCircle.style.background = `conic-gradient(#95a5a6 0deg, #95a5a6 180deg, #ecf0f1 180deg)`;
            safeSetTextContent('trustPercentage', 'N/A');
            safeSetTextContent('trustStatus', 'Nivel de Reputación: Desconocido');
            safeSetTextContent('trustDescription', 'No se pueden obtener datos de reputación en este momento.');
            return;
        }

        const confidence = abuseipdb.abuse_confidence || 0;
        const reports = abuseipdb.total_reports || 0;
        const isWhitelisted = abuseipdb.is_whitelisted;

        let reputationLevel = '';
        let reputationScore = 0;
        let color = '#2ecc71';
        let description = '';

        if (isWhitelisted) {
            reputationLevel = 'Excelente';
            reputationScore = 100;
            color = '#27ae60';
            description = 'IP verificada como segura y confiable por AbuseIPDB.';
        } else if (confidence === 0 && reports === 0) {
            reputationLevel = 'Alta';
            reputationScore = 95;
            color = '#2ecc71';
            description = 'Sin reportes de abuso ni actividad sospechosa detectada.';
        } else if (confidence === 0 && reports <= 5) {
            reputationLevel = 'Alta';
            reputationScore = 85;
            color = '#2ecc71';
            description = `Algunos reportes históricos (${reports}) pero sin confianza de abuso actual.`;
        } else if (confidence === 0 && reports <= 50) {
            reputationLevel = 'Media-Alta';
            reputationScore = 75;
            color = '#27ae60';
            description = `Reportes históricos moderados (${reports}) pero sin amenaza actual.`;
        } else if (confidence === 0 && reports > 50) {
            reputationLevel = 'Media';
            reputationScore = 60;
            color = '#f39c12';
            description = `Muchos reportes históricos (${reports}) pero sin actividad reciente maliciosa.`;
        } else if (confidence > 0 && confidence <= 25) {
            reputationLevel = 'Media';
            reputationScore = Math.max(40, 75 - confidence);
            color = '#f39c12';
            description = `Confianza de abuso baja (${confidence}%) con ${reports} reportes.`;
        } else if (confidence > 25 && confidence <= 50) {
            reputationLevel = 'Media-Baja';
            reputationScore = Math.max(25, 50 - confidence);
            color = '#e67e22';
            description = `Confianza de abuso moderada (${confidence}%) - precaución recomendada.`;
        } else if (confidence > 50 && confidence <= 75) {
            reputationLevel = 'Baja';
            reputationScore = Math.max(15, 75 - confidence);
            color = '#e74c3c';
            description = `Alta confianza de abuso (${confidence}%) - IP potencialmente peligrosa.`;
        } else {
            reputationLevel = 'Muy Baja';
            reputationScore = Math.max(5, 100 - confidence);
            color = '#c0392b';
            description = `Confianza de abuso muy alta (${confidence}%) - IP altamente peligrosa.`;
        }

        // Actualizar círculo
        const angle = (reputationScore / 100) * 360;
        if (trustCircle) {
            trustCircle.style.background = `conic-gradient(${color} 0deg, ${color} ${angle}deg, #ecf0f1 ${angle}deg)`;
        }
        safeSetTextContent('trustPercentage', `${reputationScore}%`);
        safeSetTextContent('trustStatus', `Nivel de Reputación: ${reputationLevel}`);
        safeSetTextContent('trustDescription', description);
    }

    function updateGeolocation(geo) {
        if (!geo || !geo.success) {
            safeSetTextContent('geoLocation', 'N/A');
            safeSetTextContent('geoLocationSub', 'N/A');
            safeSetTextContent('geoProvider', 'N/A');
            safeSetTextContent('geoProviderSub', 'N/A');
            safeSetTextContent('geoCoordsNew', 'N/A');
            safeSetTextContent('geoCoordsSub', 'N/A');
            safeSetTextContent('geoTimezoneNew', 'N/A');
            return;
        }

        safeSetTextContent('geoLocation', geo.city);
        safeSetTextContent('geoLocationSub', `${geo.region}, ${geo.country}`);
        safeSetTextContent('geoProvider', geo.isp);
        safeSetTextContent('geoProviderSub', geo.org);
        safeSetTextContent('geoCoordsNew', `${geo.latitude}`);
        safeSetTextContent('geoCoordsSub', `${geo.longitude}`);
        safeSetTextContent('geoTimezoneNew', geo.timezone);

        // Actualizar mapa
        updateMap(geo.latitude, geo.longitude, geo.city);
    }

    function updateMap(lat, lng, city) {
        const mapContainer = document.getElementById('map');
        if (!mapContainer) return;

        mapContainer.innerHTML = '';

        if (lat && lng && lat !== 'N/A' && lng !== 'N/A') {
            try {
                map = L.map('map', {
                    zoomControl: true,
                    scrollWheelZoom: false,
                    doubleClickZoom: false,
                    dragging: false,
                    attributionControl: true
                }).setView([lat, lng], 6);
                
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors',
                    maxZoom: 19,
                    tileSize: 256,
                    zoomOffset: 0,
                    detectRetina: true,
                    crossOrigin: true
                }).addTo(map);

                setTimeout(() => {
                    if (map) {
                        map.invalidateSize();
                    }
                }, 200);

                const customIcon = L.divIcon({
                    className: 'custom-map-marker',
                    html: '<div class="marker-pin-new"></div>',
                    iconSize: [30, 30],
                    iconAnchor: [15, 15]
                });

                marker = L.marker([lat, lng], { icon: customIcon }).addTo(map);

            } catch (error) {
                console.log('Error cargando Leaflet, usando mapa estático:', error);
                createStaticMap(lat, lng, city);
            }
        }
    }

    function createStaticMap(lat, lng, city) {
        const mapContainer = document.getElementById('map');
        
        const iframe = document.createElement('iframe');
        iframe.style.width = '100%';
        iframe.style.height = '350px';
        iframe.style.border = 'none';
        iframe.style.borderRadius = '12px';
        iframe.src = `https://www.openstreetmap.org/export/embed.html?bbox=${lng-0.1},${lat-0.1},${lng+0.1},${lat+0.1}&layer=mapnik&marker=${lat},${lng}`;
        
        mapContainer.appendChild(iframe);
    }



});