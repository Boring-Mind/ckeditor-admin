var hashtags_input = document.querySelector("input#hashtags_input")
tagify = new Tagify(hashtags_input, {
    maxTags: 5,
    placeholder: "E.g. 'Machine Learning' or 'CI/CD'",
    pattern: /^[a-zA-Z0-9 \/-]{0,30}$/
})