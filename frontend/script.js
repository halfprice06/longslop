async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    
    if (!message) return;

    // Clear input
    input.value = '';

    try {
        // Replace with your actual API endpoint
        const response = await fetch('http://localhost:8000/your-endpoint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        });

        const data = await response.json();
        // Handle the response
        console.log(data);
        
    } catch (error) {
        console.error('Error:', error);
    }
} 