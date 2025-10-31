// app/static/js/detail.js
document.addEventListener('DOMContentLoaded', () => {
    // Select all the elements we'll need
    const modal = document.getElementById('image-viewer-modal');
    if (!modal) return; // Exit if the modal isn't on the page

    const modalImage = document.getElementById('modal-full-image');
    const closeBtn = modal.querySelector('.modal-close-btn');
    const clickableThumbs = document.querySelectorAll('.clickable-thumb');

    // Function to open the modal
    const openModal = (imgSrc) => {
        modalImage.src = imgSrc;
        modal.style.display = 'flex'; // Use flex to center the content
    };

    // Function to close the modal
    const closeModal = () => {
        modal.style.display = 'none';
        modalImage.src = ""; // Clear src to stop loading if in progress
    };

    // Add a click event to each thumbnail
    clickableThumbs.forEach(thumb => {
        thumb.addEventListener('click', () => {
            openModal(thumb.src);
        });
    });

    // Add event listeners for closing the modal
    closeBtn.addEventListener('click', closeModal);

    // Close when clicking on the dark background
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    // Close when pressing the 'Escape' key
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && modal.style.display === 'flex') {
            closeModal();
        }
    });
});
