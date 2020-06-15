var hashtags_input = document.querySelector("input#hashtags_input")
tagify = new Tagify(hashtags_input, {
    maxTags: 5,
    placeholder: 'Add a tag...',
    pattern: /^[a-zA-Z0-9 \/-]{0,30}$/
})