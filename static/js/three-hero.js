(function () {
    const canvas = document.getElementById("hero3d");
    if (!canvas || typeof THREE === "undefined") {
        return;
    }

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    camera.position.z = 4;

    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);

    const group = new THREE.Group();
    scene.add(group);

    const geometry = new THREE.IcosahedronGeometry(1.25, 2);
    const material = new THREE.MeshStandardMaterial({
        color: 0x22d3ee,
        wireframe: true,
        emissive: 0x0ea5b7,
        emissiveIntensity: 0.3,
        metalness: 0.1,
        roughness: 0.3,
    });
    const orb = new THREE.Mesh(geometry, material);
    group.add(orb);

    const starsGeometry = new THREE.BufferGeometry();
    const starCount = 160;
    const positions = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 8;
        positions[i + 1] = (Math.random() - 0.5) * 8;
        positions[i + 2] = (Math.random() - 0.5) * 8;
    }
    starsGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

    const starsMaterial = new THREE.PointsMaterial({
        color: 0xa5f3fc,
        size: 0.03,
        transparent: true,
        opacity: 0.9,
    });
    const stars = new THREE.Points(starsGeometry, starsMaterial);
    group.add(stars);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.65);
    scene.add(ambientLight);

    const pointLight = new THREE.PointLight(0x67e8f9, 1.15);
    pointLight.position.set(2, 3, 4);
    scene.add(pointLight);

    const animate = () => {
        orb.rotation.x += 0.003;
        orb.rotation.y += 0.004;
        stars.rotation.y -= 0.0009;
        stars.rotation.x += 0.0006;
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
    };

    animate();

    window.addEventListener("resize", () => {
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;
        if (!width || !height) {
            return;
        }
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    });
})();
