var hashtags_input = document.querySelector("input#hashtags_input")
tagify = new Tagify(hashtags_input, {
    maxTags: 5,
    placeholder: "E.g. 'Machine Learning' or 'CI/CD'",
    pattern: /^[a-zA-Z0-9 \/-]{0,30}$/
});

async function getTags() {
    const url = 'http://127.0.0.1:8000/tags/get/'
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    return await response.json();
}

document.addEventListener("DOMContentLoaded", function() {
    getTags()
    .then(whitelist => {
        tagify.settings.whitelist = whitelist['values'];
    })
});