---
---

-   Callbacks work but are hard to read and debug
    -   Which means they only "work" in a limited sense
-   Promises were added to JavaScript in 2015
    -   As in, "We promise to do this later"
-   Show how they work by creating a <g key="class">class</g> of our own called `Pledge`
    -   Based on [Trey Huffine][huffine-trey]'s [tutorial][huffine-promises]

## How can we manage asynchronous execution?

-   Most functions execute in order
    -   `Array.forEach` does something once for each element of an array but doesn't build a new array like `Array.filter`

<%- include('/inc/multi.html', {pat: 'not-callbacks-alone.*', fill: 'js out'}) %>

-   A handful of built-in functions delay execution
    -   `setTimeout` runs a callback after a certain number of milliseconds
    -   First argument is a function of no arguments
    -   Second is the delay

<%- include('/inc/fig.html', {
    id: 'promises-set-timeout',
    img: '/static/tools-small.jpg',
    alt: 'Setting a timeout',
    cap: 'Using <code>setTimeout</code> to delay operations.',
    fixme: true
}) %>

<%- include('/inc/multi.html', {pat: 'callbacks-with-timeouts.*', fill: 'js out'}) %>

-   Setting a timeout of zero defers execution without delay
    -   Which gives something else a chance to run

<%- include('/inc/multi.html', {pat: 'callbacks-with-zero-timeouts.*', fill: 'js out'}) %>

-   We can use this to build a generic <g key="non_blocking_execution">non-blocking function</g>

<%- include('/inc/multi.html', {pat: 'non-blocking.*', fill: 'js out'}) %>

<%- include('/inc/fig.html', {
    id: 'promises-set-three-delays',
    img: '/static/tools-small.jpg',
    alt: 'Delaying three function calls',
    cap: 'Order of operations with three delays function calls.',
    fixme: true
}) %>

-   Why bother?
    -   Because we may want to give something else a chance to run
-   Node provides `setImmediate` to do this for us
    -   And also `process.nextTick`, which doesn't do quite the same thing

<%- include('/inc/multi.html', {pat: 'set-immediate.*', fill: 'js out'}) %>

## How do promises work?

-   Start by showing how we want to use it

<%- include('/inc/multi.html', {pat: 'use-pledge-motivation.*', fill: 'js out'}) %>

-   Create a new `Pledge` with a callback that takes `resolve` (everything worked) and `reject` (something failed)
    -   That top-level callback does the first part of what we want to do (the part before we expect a delay)
    -   For demonstration purposes, we will use `setTimeout` to defer execution
    -   Then call to `resolve` to trigger whatever comes next
-   Look at the line with `then`
    -   This is a call to a <g key="method">method</g> of the `Pledge` object
    -   Its argument is a callback that gets the value passed to `resolve`
    -   This is where and how we handle the delayed execution.

<%- include('/inc/fig.html', {
    id: 'promises-resolve',
    img: '/static/tools-small.jpg',
    alt: 'How promises resolve',
    cap: 'Order of operations when a promise resolves.',
    fixme: true
}) %>

-   `Pledge`'s <g key="constructor">constructor</g> requires a single function called `action`
-   This function must take take two callbacks as arguments
    -   What to do if the action completes successfully
    -   What to do if it doesn't (i.e., how to handle errors)
    -   `Pledge` will provide both of these callbacks to the action at the right time
-   Give the class two methods:
    -   `then` to enable more actions
    -   `catch` to handle errors
    -   We arbitrarily decide that we can have as many `then`s as we want, but only one `catch`
-   If the action completes successfully, it gives us a value
-   We pass this value to the first `then`, pass the result of that `then` to the second one, etc.
-   If any of them fail, we pass the <g key="exception">exception</g> to the error handler

<%- include('/inc/file.html', {file: 'pledge.js'}) %>

-   There is one unfortunate trick: `bind`.
    -   When we create an object `obj` and call a method `meth`, JavaScript sets `this` inside `meth`
    -   If we use a method as a callback, `this` isn't set
    -   To convert the method to a plain old function with the right `this`, we have to use `bind`
    -   See [the documentation][bind-docs] for details
-   Let's create a pledge and return a value

<%- include('/inc/multi.html', {pat: 'use-pledge-return.*', fill: 'js out'}) %>

-   Why didn't this work?
    1.  We don't use `return` with pledges, we call `resolve` or `reject`
    2.  We haven't done anything that defers execution
    -   Our original motivating example got this right
-   A more complex example showing how to chain things

<%- include('/inc/multi.html', {pat: 'use-pledge-chained.*', fill: 'js out'}) %>

-   And finally an example where we explicitly signal a problem by calling `reject`

<%- include('/inc/multi.html', {pat: 'use-pledge-reject.*', fill: 'js out'}) %>

## How are real promises different?

-   Let's rewrite our chained pledge with built-in promises

<%- include('/inc/multi.html', {pat: 'use-promise-chained.*', fill: 'js out'}) %>

-   It's almost the same, but the callbacks run *after* the main script finishes
-   Common pattern is to return another promise from inside `then`
    -   So the next `then` is called on the returned promise, not on the original promise

<%- include('/inc/multi.html', {pat: 'promise-example.*', fill: 'js out'}) %>

<%- include('/inc/fig.html', {
    id: 'promises-chained',
    img: '/static/tools-small.jpg',
    alt: 'Chained promises',
    cap: 'Chaining promises to make asynchronous operations depend on each other.',
    fixme: true
}) %>

-   If we use a <g key="promisification">promisified</g> function from the library, we get a promise for free
-   If we want to plug in our own asynchronous functions, we need to create promises
-   If our code can run synchronously, just put it in `then`

## How can we build tools with promises?

-   Use this to build a line-counting program
-   Use the promisified version of `fs-extra`
    -   Turns all of the callbacks into promises for us

<%- include('/inc/multi.html', {pat: 'count-lines-single-file.*', fill: 'js sh out'}) %>

::: callout
### Character encoding

A <g key="character_encoding">character encoding</g> specifies how characters are stored as bytes.
The most widely used is <g key="utf_8">UTF-8</g>,
which stores characters common in Western European languages in a single byte
and uses multi-byte sequences for other symbols.
If we don't specify a character encoding,
`fs.readFileAsync` gives us an array of bytes rather than an array of characters.
:::

-   We can use `glob-promise` to delay handling the output of `glob`
    -   Use `Promise.all` to handle all the promises in an array
    -   For readability, put the creation of the promise in a separate function

<%- include('/inc/multi.html', {pat: 'count-lines-globbed-files.*', fill: 'js sh slice.out'}) %>

-   But we want to display filenames as well as counts
-   So we construct temporary objects that have the information we need downstream
    -   Use object with named fields instead of array with positional values
    -   It allows us to add or move fields without breaking code quite as often

<%- include('/inc/file.html', {file: 'count-lines-print-filenames.js'}) %>

<%- include('/inc/fig.html', {
    id: 'promises-temporary-named-fields',
    img: '/static/tools-small.jpg',
    alt: 'Temporary objects with named fields',
    cap: 'Creating temporary objects with named fields to carry values forward.',
    fixme: true
}) %>

-   Works until we run into a directory whose name name matches `*.*`
    -   Which we do in `node_modules`
-   Need to use a `stat` call to check if something is a file or not
    -   But `stat` returns a stats object that doesn't include the file's name
    -   So we create a pair to pass down the chain
    -   Use `{filename, stats}` to give the objects keys and values that match up

<%- include('/inc/multi.html', {pat: 'count-lines-with-stat.*', fill: 'js sh slice.out'}) %>

-   This is complex, but a lot simpler than it would be if we were using callbacks

## How can we make this more readable?

-   Modern JavaScript provides `async` and `await` keywords
    -   `async` means "this function implicitly returns a promise"
    -   `await` means "wait for a promise to resolve"
-   We can only use `await` inside a function that is declared to be `async`
-   Do all the same things as the explicit promise-based version, but easier to read
    -   In particular, allows us to mix asynchronous and synchronous code (`hashPath` doesn't delay computation)
-   Use these with the promisified version of the `fs` library
    -   Don't have to wrap the sliced text in a promise: that happens automatically because the function is `async`
    -   Can't `await` in the main body at the bottom because `await` only works *inside* `async` functions

<%- include('/inc/multi.html', {pat: 'await-fs.*', fill: 'js out'}) %>

-   Modify the two helper functions to look like they're waiting for results and returning them
    -   Except they actually wrap their results in promises and return those

<%- include('/inc/keep.html', {file: 'count-lines-with-stat-async.js', key: 'recycle'}) %>

-   Modify `main` to wait for things to complete
    -   Must still use `Promise.all` for collections of things
    -   `async` and `await` hide promises until they don't

<%- include('/inc/keep.html', {file: 'count-lines-with-stat-async.js', key: 'main'}) %>

## How can we handle errors with asynchronous code?

-   We created several intermediate variables in the line-counting example to make the steps clearer
-   Doing this also helps with error handling
-   If we return a promise that fails without using `await`, the error happens outside our function
    -   The failed promise is turned into an error
    -   Our `try`/`catch` doesn't help us

<%- include('/inc/multi.html', {pat: 'return-immediately.*', fill: 'js out'}) %>

-   If we `return await`, the function waits until the promise runs
    -   The promise is then turned into an exception because it failed
    -   And we're inside the scope of our error handler, which catches it

<%- include('/inc/multi.html', {pat: 'return-await.*', fill: 'js out'}) %>

-   Better practice is to be consistent and always return something
    -   Because the function is declared `async`,
        the `Error` is automatically wrapped in a promise so we can use `.then` and `.catch`

<%- include('/inc/multi.html', {pat: 'assign-immediately.*', fill: 'js out'}) %>