<template>
  <div ref="container" class="skilltree-3d"></div>
  <div v-if="selected" class="skilltree-label">
    <div class="skilltree-title">{{ selected.title }}</div>
    <div class="skilltree-desc">{{ selected.desc }}</div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import nodesData from '@/assets/skilltree_nodes_3d.json'

const container = ref(null)
const selected = ref(null)

let renderer
let scene
let camera
let controls
let animationId
let raycaster
let pointer

const nodeMeshes = new Map()

const nodes = nodesData.nodes || []

const buildLabel = (node) => {
  const parts = [node.desc1, node.desc2].filter(Boolean)
  return {
    title: node.title || node.label || 'Node',
    desc: parts.length ? parts.join(' ') : node.label || ''
  }
}

const initScene = (el) => {
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0b0e12)

  const width = el.clientWidth
  const height = el.clientHeight

  camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000)
  camera.position.set(0, -200, 140)

  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setPixelRatio(window.devicePixelRatio || 1)
  renderer.setSize(width, height)
  el.appendChild(renderer.domElement)

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.08

  const ambient = new THREE.AmbientLight(0xffffff, 0.6)
  scene.add(ambient)

  const directional = new THREE.DirectionalLight(0xffffff, 0.8)
  directional.position.set(50, -80, 120)
  scene.add(directional)

  raycaster = new THREE.Raycaster()
  pointer = new THREE.Vector2()

  addNodes()
  addConnections()

  renderer.domElement.addEventListener('pointerdown', onPointerDown)
  window.addEventListener('resize', onResize)

  animate()
}

const addNodes = () => {
  const geometry = new THREE.SphereGeometry(2.2, 16, 16)

  nodes.forEach((node) => {
    const z = node.z3 ?? 0
    const t = Math.max(0, Math.min(1, z / 80))
    const color = new THREE.Color().setHSL(0.62 - t * 0.35, 0.85, 0.55)
    const material = new THREE.MeshStandardMaterial({ color })

    const mesh = new THREE.Mesh(geometry, material)
    mesh.position.set(node.x3, node.y3, node.z3)
    mesh.userData = { id: node.id, node }
    nodeMeshes.set(node.id, mesh)
    scene.add(mesh)
  })
}

const addConnections = () => {
  const lineMaterial = new THREE.LineBasicMaterial({ color: 0x2a5b7a })
  const seen = new Set()

  nodes.forEach((node) => {
    const from = nodeMeshes.get(node.id)
    if (!from) return

    const connections = node.connections || []
    connections.forEach((targetId) => {
      const key = [node.id, targetId].sort().join('::')
      if (seen.has(key)) return
      seen.add(key)

      const to = nodeMeshes.get(targetId)
      if (!to) return

      const points = [from.position, to.position]
      const geometry = new THREE.BufferGeometry().setFromPoints(points)
      const line = new THREE.Line(geometry, lineMaterial)
      scene.add(line)
    })
  })
}

const onPointerDown = (event) => {
  if (!renderer || !camera) return
  const rect = renderer.domElement.getBoundingClientRect()
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(pointer, camera)
  const intersects = raycaster.intersectObjects(Array.from(nodeMeshes.values()))
  if (intersects.length === 0) return

  const hit = intersects[0].object
  const info = hit.userData?.node
  if (!info) return

  selected.value = buildLabel(info)

  nodeMeshes.forEach((mesh) => {
    mesh.scale.setScalar(mesh === hit ? 1.4 : 1)
  })
}

const onResize = () => {
  if (!renderer || !camera || !container.value) return
  const width = container.value.clientWidth
  const height = container.value.clientHeight
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

const animate = () => {
  animationId = requestAnimationFrame(animate)
  controls.update()
  renderer.render(scene, camera)
}

onMounted(() => {
  if (container.value) {
    initScene(container.value)
  }
})

onBeforeUnmount(() => {
  if (renderer) {
    renderer.domElement.removeEventListener('pointerdown', onPointerDown)
  }
  window.removeEventListener('resize', onResize)
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  if (renderer) {
    renderer.dispose()
  }
  nodeMeshes.clear()
})
</script>

<style scoped>
.skilltree-3d {
  width: 100%;
  height: 100%;
  min-height: 520px;
  position: relative;
}

.skilltree-label {
  position: absolute;
  left: 16px;
  bottom: 16px;
  background: rgba(8, 12, 16, 0.9);
  border: 1px solid rgba(60, 120, 160, 0.6);
  padding: 12px 14px;
  max-width: 320px;
  color: #dfefff;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 13px;
}

.skilltree-title {
  font-weight: 600;
  margin-bottom: 6px;
}

.skilltree-desc {
  color: #b8d6ea;
}
</style>
