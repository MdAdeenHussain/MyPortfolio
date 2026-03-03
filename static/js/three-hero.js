import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import SplineLoader from "@splinetool/loader";

const container = document.getElementById("hero3dContainer");

if (container) {
    const getContainerSize = () => ({
        width: Math.max(320, container.clientWidth || window.innerWidth),
        height: Math.max(260, container.clientHeight || window.innerHeight),
    });

    const initialSize = getContainerSize();

    const camera = new THREE.OrthographicCamera(
        initialSize.width / -2,
        initialSize.width / 2,
        initialSize.height / 2,
        initialSize.height / -2,
        -50000,
        10000
    );
    camera.position.set(0, 0, 0);
    camera.quaternion.setFromEuler(new THREE.Euler(0, 0, 0));

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#e9e2db");

    const loader = new SplineLoader();
    loader.load("https://prod.spline.design/qZ1os9kUc3dzmdcN/scene.splinecode", (splineScene) => {
        scene.add(splineScene);
    });

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(initialSize.width, initialSize.height);
    renderer.setAnimationLoop(animate);

    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;
    renderer.setClearAlpha(1);

    container.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.125;
    controls.enablePan = false;
    controls.enableZoom = false;

    window.addEventListener("resize", onWindowResize);

    function onWindowResize() {
        const { width, height } = getContainerSize();
        camera.left = width / -2;
        camera.right = width / 2;
        camera.top = height / 2;
        camera.bottom = height / -2;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
    }

    function animate() {
        controls.update();
        renderer.render(scene, camera);
    }
}
