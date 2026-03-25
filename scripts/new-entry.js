#!/usr/bin/env node

/**
 * Script para crear una nueva entrada de la bitácora.
 * 
 * Uso:
 *   node scripts/new-entry.js "Título de la entrada"
 *   node scripts/new-entry.js "Título de la entrada" --week 2
 * 
 * Genera:
 *   - entries/{slug}/metadata.json
 *   - entries/{slug}/main.md
 *   - figures/{slug}/metadata.json (incluye el notebook .ipynb)
 *   - notebooks/{slug}.ipynb
 *   - Actualiza entries/index.json
 */

import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import crypto from 'crypto'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const ROOT = path.resolve(__dirname, '..')

const ENTRIES_DIR = path.join(ROOT, 'entries')
const FIGURES_DIR = path.join(ROOT, 'figures')
const NOTEBOOKS_DIR = path.join(ROOT, 'notebooks')
const INDEX_FILE = path.join(ENTRIES_DIR, 'index.json')

function shortCellId() {
  return crypto.randomBytes(4).toString('hex')
}

function toSlug(text) {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, '')
    .trim()
    .replace(/\s+/g, '_')
}

function getNextNumber() {
  if (!fs.existsSync(INDEX_FILE)) return 1
  
  const index = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf-8'))
  if (!Array.isArray(index) || index.length === 0) return 1
  
  const numbers = index
    .map(slug => {
      const match = slug.match(/^(\d+)-/)
      return match ? parseInt(match[1], 10) : 0
    })
    .filter(n => n > 0)
  
  return numbers.length > 0 ? Math.max(...numbers) + 1 : 1
}

function getTodayDate() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function createMetadata(title, weekNumber) {
  return {
    entry_title: title,
    date: getTodayDate(),
    summary: '',
    adjoined_files: {},
    tasks: {
      'Tarea de ejemplo': {
        status: 'to-do',
        type: 'writing',
        description: '',
        comments: {}
      }
    },
    extra: {}
  }
}

function createMarkdown(title) {
  return `# ${title}

Describe aquí el trabajo realizado esta semana.

## Lo que hice

- 

## Reflexiones

- 

## Próximos pasos

- 
`
}

function createFiguresMetadata(slug) {
  const notebookFile = `${slug}.ipynb`
  return {
    [notebookFile]: {
      caption: 'Notebook de la investigación.'
    }
  }
}

function createNotebookSkeleton(title) {
  const date = getTodayDate()
  return {
    cells: [
      {
        cell_type: 'markdown',
        id: shortCellId(),
        metadata: {},
        source: [`# ${title}\n`, '\n', `**Fecha:** ${date}\n`]
      }
    ],
    metadata: {
      kernelspec: {
        display_name: 'Python 3',
        language: 'python',
        name: 'python3'
      },
      language_info: {
        name: 'python',
        version: '3.12.0'
      }
    },
    nbformat: 4,
    nbformat_minor: 5
  }
}

function updateIndex(slug) {
  let index = []
  
  if (fs.existsSync(INDEX_FILE)) {
    index = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf-8'))
  }
  
  if (!index.includes(slug)) {
    index.push(slug)
    index.sort()
  }
  
  fs.writeFileSync(INDEX_FILE, JSON.stringify(index, null, 2) + '\n')
}

function main() {
  const args = process.argv.slice(2)
  
  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
Uso: node scripts/new-entry.js "Título de la entrada"

Opciones:
  --week <n>    Número de semana (opcional, se calcula automáticamente)
  --help, -h    Muestra esta ayuda

Ejemplo:
  node scripts/new-entry.js "Segunda semana de investigación"
`)
    process.exit(0)
  }
  
  const title = args[0]
  let weekNumber = null
  
  const weekIndex = args.indexOf('--week')
  if (weekIndex !== -1 && args[weekIndex + 1]) {
    weekNumber = parseInt(args[weekIndex + 1], 10)
  }
  
  const number = weekNumber || getNextNumber()
  const paddedNumber = String(number).padStart(3, '0')
  const slugBase = toSlug(title)
  const slug = `${paddedNumber}-${slugBase}`
  
  const entryDir = path.join(ENTRIES_DIR, slug)
  const figuresDir = path.join(FIGURES_DIR, slug)
  const notebookPath = path.join(NOTEBOOKS_DIR, `${slug}.ipynb`)
  
  if (fs.existsSync(entryDir)) {
    console.error(`Error: La entrada "${slug}" ya existe.`)
    process.exit(1)
  }
  
  if (fs.existsSync(notebookPath)) {
    console.error(`Error: Ya existe el notebook "${notebookPath}".`)
    process.exit(1)
  }
  
  if (fs.existsSync(figuresDir)) {
    console.error(`Error: Ya existe la carpeta de figuras "${figuresDir}".`)
    process.exit(1)
  }
  
  // Crear directorios
  fs.mkdirSync(entryDir, { recursive: true })
  fs.mkdirSync(figuresDir, { recursive: true })
  
  // Crear metadata.json de la entrada
  const metadata = createMetadata(title, number)
  fs.writeFileSync(
    path.join(entryDir, 'metadata.json'),
    JSON.stringify(metadata, null, 2) + '\n'
  )
  
  // Crear main.md
  const markdown = createMarkdown(title)
  fs.writeFileSync(path.join(entryDir, 'main.md'), markdown)
  
  // figures/{slug}/metadata.json (mismo esquema que captions en PNG/HTML)
  const figuresMetadata = createFiguresMetadata(slug)
  fs.writeFileSync(
    path.join(figuresDir, 'metadata.json'),
    JSON.stringify(figuresMetadata, null, 4) + '\n'
  )
  
  // Notebook vacío con el mismo nombre que el slug
  const notebook = createNotebookSkeleton(title)
  fs.writeFileSync(notebookPath, JSON.stringify(notebook, null, 2) + '\n')
  
  // Actualizar index.json
  updateIndex(slug)
  
  console.log(`
✓ Entrada creada exitosamente!

  Slug:     ${slug}
  Entrada:  entries/${slug}/
  Figuras:  figures/${slug}/
  Notebook: notebooks/${slug}.ipynb

Archivos creados:
  - entries/${slug}/metadata.json
  - entries/${slug}/main.md
  - figures/${slug}/metadata.json
  - notebooks/${slug}.ipynb

Próximos pasos:
  1. Edita entries/${slug}/metadata.json para ajustar tareas o adjuntos
  2. Escribe el contenido en entries/${slug}/main.md
  3. Trabaja en notebooks/${slug}.ipynb y añade figuras en figures/${slug}/
`)
}

main()
