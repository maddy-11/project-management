// Expand/collapse logic for folders in the document tree with persistent state using event delegation
function getCollapsedFolders() {
  try {
    return JSON.parse(localStorage.getItem('collapsedFolders') || '[]');
  } catch (e) {
    return [];
  }
}
function setCollapsedFolders(arr) {
  localStorage.setItem('collapsedFolders', JSON.stringify(arr));
}
function isCollapsed(folderId) {
  return getCollapsedFolders().includes(folderId);
}
function toggleCollapsed(folderId) {
  let arr = getCollapsedFolders();
  if (arr.includes(folderId)) {
    arr = arr.filter(id => id !== folderId);
  } else {
    arr.push(folderId);
  }
  setCollapsedFolders(arr);
}
function restoreExpandCollapseState() {
  document.querySelectorAll('li.folder-item').forEach(function(li) {
    const folderId = li.getAttribute('data-id');
    const childrenUl = document.querySelector(`.folder-children[data-parent="${folderId}"]`);
    const icon = li.querySelector('.expand-icon i');
    if (!childrenUl || !icon) return;
    if (isCollapsed(folderId)) {
      childrenUl.style.display = 'none';
      icon.classList.remove('fa-chevron-down');
      icon.classList.add('fa-chevron-right');
    } else {
      childrenUl.style.display = '';
      icon.classList.remove('fa-chevron-right');
      icon.classList.add('fa-chevron-down');
    }
  });
}
function initExpandCollapse() {
  restoreExpandCollapseState();
  // Attach event delegation only once
  if (!window.expandCollapseDelegationAttached) {
    document.addEventListener('click', function(e) {
      const icon = e.target.closest('.expand-icon');
      if (!icon) return;
      const li = icon.closest('li.folder-item');
      const folderId = li.getAttribute('data-id');
      const childrenUl = document.querySelector(`.folder-children[data-parent="${folderId}"]`);
      if (!childrenUl) return;
      if (childrenUl.style.display === 'none') {
        childrenUl.style.display = '';
        icon.querySelector('i').classList.remove('fa-chevron-right');
        icon.querySelector('i').classList.add('fa-chevron-down');
      } else {
        childrenUl.style.display = 'none';
        icon.querySelector('i').classList.remove('fa-chevron-down');
        icon.querySelector('i').classList.add('fa-chevron-right');
      }
      toggleCollapsed(folderId);
    });
    window.expandCollapseDelegationAttached = true;
  }
}
// Always call after tree loads or reloads
if (typeof window.initExpandCollapseLoaded === 'undefined') {
  window.initExpandCollapseLoaded = true;
  document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.expand-icon')) {
      initExpandCollapse();
    }
  });
}

// Document delete logic
function attachDocumentDeleteHandlers() {
  document.addEventListener('click', function(e) {
    const btn = e.target.closest('.delete-document-btn');
    if (!btn) return;
    const li = btn.closest('li.doc-tree-item');
    if (!li) return;
    const docId = li.getAttribute('data-id').replace('doc-', '');
    if (!confirm('Are you sure you want to delete this document?')) return;
    fetch('/documents/delete/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': (document.querySelector('[name=csrfmiddlewaretoken]') || {}).value || ''
      },
      body: JSON.stringify({ type: 'document', id: docId })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        // Replace the tree with the updated HTML
        const tree = document.getElementById('docTree');
        if (tree && data.tree) tree.outerHTML = data.tree;
        // Re-attach handlers
        attachDocumentDeleteHandlers();
      } else {
        alert(data.message || 'Error deleting document.');
      }
    })
    .catch(() => alert('Error deleting document.'));
  });
}

document.addEventListener('DOMContentLoaded', function() {
  attachDocumentDeleteHandlers();
});

// jQuery AJAX handler for document delete form
if (window.jQuery) {
  $(document).on('submit', '.delete-document-form', function(e) {
    e.preventDefault();
    if (!confirm('Are you sure you want to delete this document?')) return;
    var $form = $(this);
    $.ajax({
      url: $form.attr('action'),
      type: 'POST',
      data: $form.serialize(),
      success: function(data) {
        if (data.status === 'success' && data.tree) {
          $('#docTree').replaceWith(data.tree);
        } else {
          alert(data.message || 'Error deleting document.');
        }
      },
      error: function() {
        alert('Error deleting document.');
      }
    });
  });
} 