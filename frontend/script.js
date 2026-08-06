// ============ CONFIGURATION ============
const API_BASE_URL = 'http://127.0.0.1:8000';
const AUTH_TOKEN = 'secret-token-123';

// ============ CATEGORY TREE DATA ============
const CATEGORY_TREE = {
    name: "All Tags",
    children: [
        { 
            name: "Work", 
            children: [
                { name: "Standups", children: [] },
                { name: "Retros", children: [] },
            ]
        },
        { 
            name: "Personal", 
            children: [
                { 
                    name: "Health", 
                    children: [
                        { name: "Fitness", children: [] },
                    ]
                },
                { name: "Recipes", children: [] },
            ]
        },
        { name: "Travel", children: [] },
    ],
};

// ============ DATA LAYER ============
async function fetchNotes(tag = null) {
    const url = tag ? `${API_BASE_URL}/notes?tag=${tag}` : `${API_BASE_URL}/notes`;
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to fetch notes: ${response.status}`);
    }
    return await response.json();
}

async function createNote(title, content, tag, ownerId) {
    const response = await fetch(`${API_BASE_URL}/notes`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, content, tag, owner_id: parseInt(ownerId) }),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Failed to create note: ${response.status}`);
    }
    return await response.json();
}

async function deleteNote(id) {
    const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
        method: 'DELETE',
        headers: {
            'x-token': AUTH_TOKEN,
        },
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Failed to delete note: ${response.status}`);
    }
    return await response.json();
}

async function updateNote(id, data) {
    const response = await fetch(`${API_BASE_URL}/notes/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || `Failed to update note: ${response.status}`);
    }
    return await response.json();
}

async function searchNotes(keyword = null, sortBy = null) {
    let url = `${API_BASE_URL}/notes/search`;
    const params = new URLSearchParams();
    if (keyword) params.append('keyword', keyword);
    if (sortBy) params.append('sort_by', sortBy);
    if (params.toString()) url += '?' + params.toString();
    
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to search notes: ${response.status}`);
    }
    return await response.json();
}

async function lookupNoteByTitle(title, algo = 'iterative') {
    const url = `${API_BASE_URL}/notes/lookup?title=${encodeURIComponent(title)}&algo=${algo}`;
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to lookup note: ${response.status}`);
    }
    return await response.json();
}

async function quickFindByTag(tag) {
    const url = `${API_BASE_URL}/notes/quick-find?tag=${encodeURIComponent(tag)}`;
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to quick find: ${response.status}`);
    }
    return await response.json();
}

async function smartSearch(query) {
    const url = `${API_BASE_URL}/notes/smart-search?q=${encodeURIComponent(query)}`;
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`Failed to smart search: ${response.status}`);
    }
    return await response.json();
}

// ============ RENDER FUNCTIONS ============

// Recursive function to render category tree
function renderCategoryTree(node, container) {
    const ul = document.createElement('ul');
    
    const li = document.createElement('li');
    
    // Toggle icon
    const toggleSpan = document.createElement('span');
    toggleSpan.className = 'toggle-icon';
    const hasChildren = node.children && node.children.length > 0;
    toggleSpan.textContent = hasChildren ? '▼' : '•';
    
    // Node label
    const labelSpan = document.createElement('span');
    labelSpan.className = 'node-label';
    labelSpan.textContent = node.name;
    
    li.appendChild(toggleSpan);
    li.appendChild(labelSpan);
    
    if (hasChildren) {
        const childrenUl = document.createElement('ul');
        childrenUl.className = 'children';
        
        // Recursively render children
        node.children.forEach(child => {
            renderCategoryTree(child, childrenUl);
        });
        
        li.appendChild(childrenUl);
        
        // Toggle click handler
        li.addEventListener('click', (e) => {
            // Don't toggle if clicking on a child's toggle
            if (e.target.closest('ul') && e.target !== toggleSpan) return;
            
            const childrenContainer = li.querySelector('ul');
            if (childrenContainer) {
                childrenContainer.classList.toggle('hidden');
                toggleSpan.textContent = childrenContainer.classList.contains('hidden') ? '▶' : '▼';
            }
        });
    }
    
    ul.appendChild(li);
    container.appendChild(ul);
}

function renderNoteCard(note) {
    const card = document.createElement('div');
    card.className = 'note-card';
    card.dataset.noteId = note.id;
    card.dataset.tag = note.tag || '';
    
    // Title
    const title = document.createElement('div');
    title.className = 'note-title';
    title.textContent = note.title;
    card.appendChild(title);
    
    // Content
    const content = document.createElement('div');
    content.className = 'note-content';
    content.textContent = note.content;
    card.appendChild(content);
    
    // Tag
    const tag = document.createElement('span');
    tag.className = 'note-tag';
    tag.textContent = note.tag || 'untagged';
    card.appendChild(tag);
    
    // Owner
    const owner = document.createElement('div');
    owner.className = 'note-owner';
    owner.textContent = `Owner: ${note.owner_id}`;
    card.appendChild(owner);
    
    // AI Suggestion (if present)
    if (note.ai_suggestion) {
        const aiDiv = document.createElement('div');
        aiDiv.className = 'ai-suggestion';
        
        const tagsDiv = document.createElement('div');
        tagsDiv.className = 'ai-tags';
        note.ai_suggestion.tags.forEach(tagName => {
            const tagSpan = document.createElement('span');
            tagSpan.className = 'ai-tag';
            tagSpan.textContent = tagName;
            tagsDiv.appendChild(tagSpan);
        });
        aiDiv.appendChild(tagsDiv);
        
        const summary = document.createElement('div');
        summary.className = 'ai-summary';
        summary.textContent = note.ai_suggestion.summary;
        aiDiv.appendChild(summary);
        
        // Apply as tag button
        const applyBtn = document.createElement('button');
        applyBtn.className = 'apply-tag-btn';
        applyBtn.textContent = 'Apply as tag';
        applyBtn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const firstTag = note.ai_suggestion.tags[0];
            if (firstTag) {
                try {
                    await updateNote(note.id, { tag: firstTag });
                    tag.textContent = firstTag;
                    card.dataset.tag = firstTag;
                    // Remove AI suggestion or update it
                    aiDiv.remove();
                    // Show success feedback
                    applyBtn.textContent = '✓ Applied!';
                    setTimeout(() => applyBtn.remove(), 2000);
                } catch (error) {
                    console.error('Failed to apply tag:', error);
                }
            }
        });
        aiDiv.appendChild(applyBtn);
        
        card.appendChild(aiDiv);
    }
    
    // Actions
    const actions = document.createElement('div');
    actions.className = 'note-actions';
    
    const deleteBtn = document.createElement('button');
    deleteBtn.className = 'delete-btn';
    deleteBtn.textContent = 'Delete';
    deleteBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to delete this note?')) {
            try {
                await deleteNote(note.id);
                card.remove();
                // Remove from DOM
            } catch (error) {
                console.error('Failed to delete note:', error);
                showError('Failed to delete note: ' + error.message);
            }
        }
    });
    actions.appendChild(deleteBtn);
    card.appendChild(actions);
    
    return card;
}

function renderNotes(notes) {
    const container = document.getElementById('notes-list');
    container.innerHTML = '';
    
    if (!notes || notes.length === 0) {
        const empty = document.createElement('p');
        empty.textContent = 'No notes found. Create your first note above!';
        empty.style.textAlign = 'center';
        empty.style.padding = '40px';
        empty.style.color = '#7f8c8d';
        container.appendChild(empty);
        return;
    }
    
    notes.forEach(note => {
        const card = renderNoteCard(note);
        container.appendChild(card);
    });
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function showFormError(message) {
    const errorDiv = document.getElementById('form-error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function hideFormError() {
    const errorDiv = document.getElementById('form-error');
    errorDiv.style.display = 'none';
}

// ============ QUICK TAG BUTTONS ============
function renderQuickTagButtons(tags) {
    const container = document.getElementById('quick-tag-buttons');
    container.innerHTML = '';
    
    tags.forEach(tag => {
        const btn = document.createElement('button');
        btn.className = 'tag-btn';
        btn.textContent = tag;
        btn.addEventListener('click', async () => {
            try {
                const result = await quickFindByTag(tag);
                if (result.found && result.note) {
                    // Highlight the note
                    const cards = document.querySelectorAll('.note-card');
                    cards.forEach(c => c.style.borderLeftColor = '#e0e0e0');
                    const targetCard = Array.from(cards).find(
                        c => parseInt(c.dataset.noteId) === result.note.id
                    );
                    if (targetCard) {
                        targetCard.style.borderLeftColor = '#e44d26';
                        targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        setTimeout(() => {
                            targetCard.style.borderLeftColor = '#e44d26';
                        }, 100);
                    }
                } else {
                    showError(`No note found with tag "${tag}"`);
                }
            } catch (error) {
                console.error('Quick find failed:', error);
                showError('Quick find failed: ' + error.message);
            }
        });
        container.appendChild(btn);
    });
}

// ============ INITIALIZATION ============
let allNotes = [];
let searchTimeout = null;
let currentFilter = null;

async function loadNotes() {
    const loading = document.getElementById('loading-message');
    const notesContainer = document.getElementById('notes-list');
    
    try {
        loading.style.display = 'block';
        notesContainer.innerHTML = '';
        
        const notes = await fetchNotes();
        allNotes = notes;
        renderNotes(notes);
        
        // Extract unique tags for quick buttons
        const tags = [...new Set(notes.map(n => n.tag).filter(t => t))];
        renderQuickTagButtons(tags);
        
        loading.style.display = 'none';
    } catch (error) {
        loading.style.display = 'none';
        showError('Failed to load notes: ' + error.message);
    }
}

// ============ EVENT LISTENERS ============

// Add note form
document.getElementById('add-note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    hideFormError();
    
    const title = document.getElementById('note-title').value.trim();
    const content = document.getElementById('note-content').value.trim();
    const tag = document.getElementById('note-tag').value.trim();
    const ownerId = document.getElementById('note-owner-id').value.trim();
    
    // Client-side validation
    if (!title) {
        showFormError('Title is required');
        return;
    }
    if (!content) {
        showFormError('Content is required');
        return;
    }
    
    try {
        const newNote = await createNote(title, content, tag || 'general', ownerId || 1);
        const card = renderNoteCard(newNote);
        document.getElementById('notes-list').appendChild(card);
        
        // Clear form
        document.getElementById('note-title').value = '';
        document.getElementById('note-content').value = '';
        document.getElementById('note-tag').value = '';
        document.getElementById('note-owner-id').value = '1';
        
        // Reload notes to update tag buttons
        await loadNotes();
        
    } catch (error) {
        showFormError('Failed to create note: ' + error.message);
    }
});

// Debounced search
document.getElementById('search-input').addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        const query = e.target.value.trim();
        const sortBy = document.getElementById('sort-select').value;
        
        if (query) {
            try {
                const results = await searchNotes(query, sortBy === 'date' ? 'date' : null);
                renderNotes(results);
            } catch (error) {
                console.error('Search failed:', error);
                showError('Search failed: ' + error.message);
            }
        } else {
            // Reload all notes
            await loadNotes();
        }
    }, 400);
});

// Sort select change
document.getElementById('sort-select').addEventListener('change', async () => {
    const query = document.getElementById('search-input').value.trim();
    const sortBy = document.getElementById('sort-select').value;
    
    if (query) {
        try {
            const results = await searchNotes(query, sortBy === 'date' ? 'date' : null);
            renderNotes(results);
        } catch (error) {
            console.error('Sort failed:', error);
            showError('Sort failed: ' + error.message);
        }
    } else {
        await loadNotes();
    }
});

// Lookup exact title
document.getElementById('lookup-btn').addEventListener('click', async () => {
    const title = document.getElementById('lookup-input').value.trim();
    const resultSpan = document.getElementById('lookup-result');
    
    if (!title) {
        resultSpan.textContent = 'Please enter a title';
        resultSpan.style.color = '#e74c3c';
        return;
    }
    
    try {
        const result = await lookupNoteByTitle(title, 'iterative');
        if (result.found && result.note) {
            resultSpan.textContent = `✓ Found: "${result.note.title}"`;
            resultSpan.style.color = '#27ae60';
            
            // Highlight the note
            const cards = document.querySelectorAll('.note-card');
            cards.forEach(c => c.style.borderLeftColor = '#e0e0e0');
            const targetCard = Array.from(cards).find(
                c => parseInt(c.dataset.noteId) === result.note.id
            );
            if (targetCard) {
                targetCard.style.borderLeftColor = '#f39c12';
                targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } else {
            resultSpan.textContent = '✗ Not found';
            resultSpan.style.color = '#e74c3c';
        }
    } catch (error) {
        resultSpan.textContent = 'Error: ' + error.message;
        resultSpan.style.color = '#e74c3c';
    }
});

// Enter key for lookup
document.getElementById('lookup-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('lookup-btn').click();
    }
});

// Smart Search
document.getElementById('smart-search-input').addEventListener('input', (e) => {
    const query = e.target.value.trim();
    const resultsDiv = document.getElementById('smart-search-results');
    
    if (!query) {
        resultsDiv.innerHTML = '';
        return;
    }
    
    // Debounce smart search
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        try {
            const result = await smartSearch(query);
            resultsDiv.innerHTML = '';
            
            if (result.results && result.results.length > 0) {
                result.results.forEach(note => {
                    const item = document.createElement('div');
                    item.className = 'smart-result-item';
                    
                    const title = document.createElement('div');
                    title.style.fontWeight = 'bold';
                    title.textContent = note.title;
                    item.appendChild(title);
                    
                    const score = document.createElement('span');
                    score.className = 'score';
                    score.textContent = `Score: ${(note.similarity_score * 100).toFixed(1)}%`;
                    item.appendChild(score);
                    
                    const content = document.createElement('div');
                    content.style.fontSize = '13px';
                    content.style.color = '#555';
                    content.textContent = note.content.substring(0, 100) + '...';
                    item.appendChild(content);
                    
                    resultsDiv.appendChild(item);
                });
            } else {
                resultsDiv.innerHTML = '<p style="color: #7f8c8d;">No results found</p>';
            }
        } catch (error) {
            resultsDiv.innerHTML = `<p style="color: #e74c3c;">Error: ${error.message}</p>`;
        }
    }, 500);
});

// ============ INITIAL LOAD ============
document.addEventListener('DOMContentLoaded', () => {
    // Render category tree
    const treeContainer = document.getElementById('category-tree');
    renderCategoryTree(CATEGORY_TREE, treeContainer);
    
    // Load notes
    loadNotes();
});

console.log('Zomato Notes initialized!');
console.log('API URL:', API_BASE_URL);
console.log('Note: All events attached via addEventListener - no inline HTML attributes used.');