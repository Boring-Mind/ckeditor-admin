var hashtags_input = document.querySelector("input#hashtags_input")
tagify = new Tagify(hashtags_input, {
    maxTags: 10,
    placeholder: 'Machine Learning',
    pattern: /^[a-zA-Z0-9 \/-@]{0,35}$/
})