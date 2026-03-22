document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.getElementById('contactForm');
    if (!contactForm) return;

    contactForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const form = e.target;
        const name = form.name.value.trim();
        const phone = form.phone.value.trim();
        const message = form.message.value.trim();
        
        // Validate fields
        if (!name || !phone || !message) {
            alert('Please fill in all fields');
            return;
        }
        
        if (!/^\d{10}$/.test(phone.replace(/[-\s]/g, ''))) {
            alert('Please enter a valid phone number');
            return;
        }
        
        const data = {
            name: name,
            phone: phone,
            message: message
        };

        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (response.ok && result.status === 'success') {
                alert('Message sent successfully! We will get back to you soon.');
                form.reset();
            } else {
                alert('Error sending message: ' + (result.message || result.error || response.statusText));
            }
        } catch (error) {
            console.error('Contact form error:', error);
            alert('Network error while sending message. Please try again.');
        }
    });
});
