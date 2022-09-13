---
template: page
title: "Page Templates"
lede: "Generating HTML pages from templates"
---

Every program needs documentation in order to be usable,
and the best place to put that documentation is on the web.
Writing and updating pages by hand is time-consuming and error-prone,
particularly when many parts are the same,
so most documentation sites use some kind of
[% i "static site generator" %][% g static_site_generator %]static site generator[% /g %][% /i %]
to create web pages from templates.

At the heart of every static site generator is a page templating system.
Thousands of these have been written in the last thirty years
in every popular programming language
(and one language, [% i "PHP" %][PHP][php][% /i %], was created for this purpose).
Most of these systems use one of three designs
([% f page-templates-options %]):

1.  Mix commands in a language such as JavaScript with the HTML or Markdown
    using some kind of marker to indicate which parts are commands
    and which parts are to be taken as-is.
    This approach is taken by [% i "EJS" %][EJS][ejs][% /i %],
    which we used to write these lessons.

2.  Create a mini-language with its own commands like [% i "Jekyll" %][Jekyll][jekyll][% /i %]
    (which is used by [% i "GitHub Pages" %][GitHub Pages][github-pages][% /i %]).
    Mini-languages are appealing because they are smaller and safer than general-purpose languages,
    but experience shows that they eventually grow
    most of the features of a general-purpose language.
    Again, some kind of marker must be used to show
    which parts of the page are code and which are ordinary text.

3.  Put directives in specially-named attributes in the HTML.
    This approach has been the least popular,
    but since pages are valid HTML,
    it eliminates the need for a special parser.

[% figure slug="page-templates-options" img="figures/options.svg" alt="Three options for page templates" caption="Three different ways to implement page templating." %]

In this chapter we will build a simple page templating system using the third strategy.
We will process each page independently by parsing the HTML
and walking the [% i "DOM" %]DOM[% /i %] to find nodes with special attributes.
Our program will execute the instructions in those nodes
to do the equivalent of loops and if/else statements;
other nodes will be copied as-is to create text.

<div class="break-before"></div>
## What will our system look like? {: #page-templates-syntax}

Let's start by deciding what "done" looks like.
Suppose we want to turn an array of strings into an HTML list.
Our page will look like this:

[% excerpt file="input-loop.html" %]

The attribute `z-loop` tells the tool to repeat the contents of that node;
the loop variable and the collection being looped over are separated by a colon.
The attribute `z-var` tells the tool to fill in the node with the value of the variable.
{: .continue}

When our tool processes this page,
the output will be standard HTML without any traces of how it was created:

[% excerpt file="output-loop.html" %]

> ### Human-readable vs. machine-readable
>
> The introduction said that mini-languages for page templating
> quickly start to accumulate extra features.
> We have already started down that road
> by putting the loop variable and loop target in a single attribute
> and splitting that attribute to get them out.
> Doing this makes loops easy for people to type,
> but hides important information from standard HTML processing tools.
> They can't know that this particular attribute of these particular elements
> contains multiple values
> or that those values should be extracted by splitting a string on a colon.
> We could instead require people to use two attributes, as in:
>
> ```html
> <ul z-loop="names" z-loop-var="item">
> ```
>
> but we have decided to err on the side of minimal typing.
> And note that strictly speaking,
> we should call our attributes `data-something` instead of `z-something`
> to conform with [% i "HTML5 specification" %][the HTML5 specification][html5-data-attributes][% /i %],
> but by the time we're finished processing our templates,
> there shouldn't be any `z-*` attributes left to confuse a browser.
{: .continue}

The next step is to define the API for filling in templates.
Our tool needs the template itself,
somewhere to write its output,
and some variables to use in the expansion.
These variables might come from a configuration file,
from a YAML header in the file itself,
or from some mix of the two;
for the moment,
we will just pass them into the expansion function as an object:

[% excerpt file="example-call.js" %]

## How can we keep track of values? {: #page-templates-values}

Speaking of variables,
we need a way to keep track of their current values;
we say "current" because the value of a loop variable changes each time we go around the loop.
We also need to maintain multiple sets of variables
so that variables used inside a loop
don't conflict with ones used outside it.
(We don't actually "need" to do this---we could just have one global set of variables---but
experience teaches us that if all our variables are global,
all of our programs will be buggy.)

The standard way to manage variables is to create a stack of lookup tables.
Each [% i "stack frame" %][% g stack_frame %]stack frame[% /g %][% /i %] is an object with names and values;
when we need to find a variable,
we look through the stack frames in order to find the uppermost definition of that variable..

> ### Scoping rules
>
> Searching the stack [% i "call stack!stack frame" "stack frame" %]frame[% /i %] by frame
> while the program is running
> is called is [% i "dynamic scoping" "scoping!dynamic" %][% g dynamic_scoping %]dynamic scoping[% /g %][% /i %],
> since we find variables while the program is running.
> In contrast,
> most programming languages used [% i "lexical scoping" "scoping!lexical" %][% g lexical_scoping %]lexical scoping[% /g %][% /i %],
> which figures out what a variable name refers to based on the structure of the program text.

The values in a running program are sometimes called
an [% i "environment (to store variables)" "call stack!environment" %][% g environment %]environment[% /g %][% /i %],
so we have named our stack-handling class `Env`.
Its methods let us push and pop new stack frames
and find a variable given its name;
if the variable can't be found,
`Env.find` returns `undefined` instead of throwing an exception
([% f page-templates-stack %]).

[% excerpt file="env.js" %]

[% figure slug="page-templates-stack" img="figures/stack.svg" alt="Variable stack" caption="Using a stack to manage variables." %]

## How do we handle nodes? {: #page-templates-nodes}

HTML pages have a nested structure,
so we will process them using
the [% i "Visitor pattern" "design pattern!Visitor" %][% g visitor_pattern %]Visitor[% /g %][% /i %] design pattern.
`Visitor`'s constructor takes the root node of the DOM tree as an argument and saves it.
When we call `Visitor.walk` without a value,
it starts recursing from that saved root;
if `.walk` is given a value (as it is during recursive calls),
it uses that instead.

[% excerpt file="visitor.js" %]

`Visitor` defines two methods called `open` and `close` that are called
when we first arrive at a node and when we are finished with it
([% f page-templates-visitor %]).
The default implementations of these methods throw exceptions
to remind the creators of derived classes to implement their own versions.
{: .continue}

[% figure slug="page-templates-visitor" img="figures/visitor.svg" alt="The Visitor pattern" caption="Using the Visitor pattern to evaluate a page template." %]

The `Expander` class is specialization of `Visitor`
that uses an `Env` to keep track of variables.
It imports a handler
for each type of special node we support---we will write those in a moment---and
uses them to process each type of node:

1.  If the node is plain text, copy it to the output.

1.  If there is a handler for the node,
    call the handler's `open` or `close` method.

1.  Otherwise, open or close a regular tag.

[% excerpt file="expander.js" omit="skip" %]

Checking to see if there is a handler for a particular node
and getting that handler are straightforward---we just
look at the node's attributes:

[% excerpt file="expander.js" keep="handlers" %]

Finally, we need a few helper methods to show tags and generate output:

[% excerpt file="expander.js" keep="helpers" %]

Notice that this class adds strings to an array and joins them all right at the end
rather than concatenating strings repeatedly.
Doing this is more efficient and also helps with debugging,
since each string in the array corresponds to a single method call.
{: .continue}

## How do we implement node handlers? {: #page-templates-handlers}

At this point
we have built a lot of infrastructure but haven't actually processed any special nodes.
To do that,
let's write a handler that copies a constant number into the output:

[% excerpt file="z-num.js" %]

When we enter a node like `<span z-num="123"/>`
this handler asks the expander to show an opening tag
followed by the value of the `z-num` attribute.
When we exit the node,
the handler asks the expander to close the tag.
The handler doesn't know whether things are printed immediately,
added to an output list,
or something else;
it just knows that whoever called it implements the low-level operations it needs.
{: .continue}

Note that this expander is *not* a class,
but instead an object with two functions stored under the keys `open` and `close`.
We could use a class for each handler
so that handlers can store any extra state they need,
but [% i "bare object" "software design!bare object" %][% g bare_object %]bare objects[% /g %][% /i %] are common and useful in JavaScript
(though we will see below that we *should* have used classes).

So much for constants; what about variables?

[% excerpt file="z-var.js" %]

This code is almost the same as the previous example.
The only difference is that instead of copying the attribute's value
directly to the output,
we use it as a key to look up a value in the environment.
{: .continue}

These two pairs of handlers look plausible, but do they work?
To find out,
we can build a program that loads variable definitions from a JSON file,
reads an HTML template,
and does the expansion:

[% excerpt file="template.js" %]

We added new variables for our test cases one by one
as we were writing this chapter.
To avoid repeating text repeatedly,
we show the entire set once:

[% excerpt file="vars.json" %]

Our first test:
is static text copied over as-is ([% f page-templates-output-static-text %])?

[% excerpt file="input-static-text.html" %]
[% excerpt file="static-text.sh" %]
[% excerpt file="output-static-text.html" %]

[% figure slug="page-templates-output-static-text" img="figures/output-static-text.svg" alt="Generating static text" caption="Static text generated by page templates." %]

Good.
Now, does the expander handle constants ([% f page-templates-output-single-constant %])?

[% excerpt file="input-single-constant.html" %]
[% excerpt file="output-single-constant.html" %]

[% figure slug="page-templates-output-single-constant" img="figures/output-single-constant.svg" alt="Generating a single constant" caption="A single constant generated by page templates." %]

What about a single variable ([% f page-templates-output-single-variable %])?

[% excerpt file="input-single-variable.html" %]
[% excerpt file="output-single-variable.html" %]

[% figure slug="page-templates-output-single-variable" img="figures/output-single-variable.svg" alt="Generating a single variable" caption="A single variable generated by page templates." %]

What about a page containing multiple variables?
There's no reason it should fail if the single-variable case works,
but we should still check---again,
software isn't done until it has been tested ([% f page-templates-output-multiple-variables %]).

[% excerpt file="input-multiple-variables.html" %]
[% excerpt file="output-multiple-variables.html" %]

[% figure slug="page-templates-output-multiple-variables" img="figures/output-multiple-variables.svg" alt="Generating multiple variables" caption="Multiple variables generated by page templates." %]

## How can we implement control flow? {: #page-templates-flow}

Our tool supports two types of control flow:
conditional expressions and loops.
Since we don't support Boolean expressions like `and` and `or`,
implementing a conditional is as simple as looking up a variable
(which we know how to do)
and then expanding the node if the value is true:

[% excerpt file="z-if.js" %]

Let's test it ([% f page-templates-output-conditional %]):

[% excerpt file="input-conditional.html" %]
[% excerpt file="output-conditional.html" %]

[% figure slug="page-templates-output-conditional" img="figures/output-conditional.svg" alt="Generating conditional text" caption="Conditional text generated by page templates." %]

<blockquote class="break-before" markdown="1">
### Spot the bug

This implementation of `if` contains a subtle bug.
The `open` and `close` functions both check the value of the control variable.
If something inside the body of the `if` changes that value,
the result could be an opening tag without a matching closing tag or vice versa.
We haven't implemented an assignment operator,
so right now there's no way for that to happen,
but it's a plausible thing for us to add later,
and tracking down a bug in old code that is revealed by new code
is always a headache.
</blockquote>

Finally we come to loops.
For these,
we need to get the array we're looping over from the environment
and do something for each of its elements.
That "something" is:

1.  Create a new stack frame holding the current value of the loop variable.

1.  Expand all of the node's children with that stack frame in place.

1.  Pop the stack frame to get rid of the temporary variable.

[% excerpt file="z-loop.js" %]

Once again,
it's not done until we test it ([% f page-templates-output-loop %]):

[% excerpt file="input-loop.html" %]
[% excerpt file="output-loop.html" %]

[% figure slug="page-templates-output-loop" img="figures/output-loop.svg" alt="Generating text with a loop" caption="Repeated text generated with a loop by page templates." %]

Notice how we create the new stack frame using:

```js
{ [indexName]: index }
```

This is an ugly but useful trick.
We can't write:
{: .continue}

```js
{ indexName: index }
```

because that would create an object with the string `indexName` as a key,
rather than one with the value of the variable `indexName` as its key.
We can't do this either:
{: .continue}

```js
{ `${indexName}`: index }
```

though it seems like we should be able to.
Instead,
we create an array containing the string we want.
Since JavaScript automatically converts arrays to strings
by concatenating their elements when it needs to,
our expression is a quick way to get the same effect as:
{: .continue}

```js
const temp = {}
temp[indexName] = index
expander.env.push(temp)
```

Those three lines *are* much easier to understand, though,
so we should probably have been less clever.
{: .continue}

## How did we know how to do all of this? {: #page-templates-learning}

We have just implemented a simple programming language.
It can't do arithmetic,
but if we wanted to add tags like:

```js
<span z-math="+"><span z-var="width"/><span z-num="1"//>
```

we could.
It's unlikely anyone would use the result---typing all of that
is so much clumsier than typing `width+1` that people wouldn't use it
unless they had no other choice---but the basic design is there.
{: .continue}

We didn't invent any of this from scratch,
any more than we invented the parsing algorithm of [% x regex-parser %].
Instead,
we did what you are doing now:
we read what other programmers had written
and tried to make sense of the key ideas.

The problem is that "making sense" depends on who we are.
When we use a low-level language,
we incur the [% i "cognitive load" %]cognitive load[% /i %] of assembling micro-steps into something more meaningful.
When we use a high-level language,
on the other hand,
we incur a similar load translating functions of functions of functions
(or meta-classes templated on object factories)
into actual operations on actual data.

More experienced programmers are more capable at both ends of the curve,
but that's not the only thing that changes.
If a novice's comprehension curve looks like the one on the left
of [% f page-templates-comprehension %],
then an expert's looks like the one on the right.
Experts don't just understand more at all levels of abstraction;
their *preferred* level has also shifted
so that \\(\sqrt{x^2 + y^2}\\)
is actually more readable than the medieval expression
"the side of the square whose area is the sum of the areas of the two squares
whose sides are given by the first part and the second part".

[% figure slug="page-templates-comprehension" img="figures/comprehension.svg" alt="Comprehension curves" caption="Novice and expert comprehension curves." %]

One implication of this is that for any given task,
the software that is quickest for a novice to comprehend
will almost certainly be different from the software that
an expert can understand most quickly.
In an ideal world our tools would automatically re-represent programs at different levels,
so that with a click of a button we could view our code as either:

```
const hosts = links.map(a => a.href.split(':')[1].split('/')[0]).unique()
```

or:

```
hosts = []
for (each a in links) do
  temp <- attr(a, 'href').split(':')[1].split('/')[0]
  if (not (temp in hosts)) do
    hosts.append(temp)
  end
end
```

just as we could change the colors used for syntax highlighting
or the depth to which loop bodies are indented.
But today's tools don't do that,
and I suspect that any IDE smart enough to translate between comprehension levels automatically
would also be smart enough to write the code without our help.

<div class="break-before"></div>
## Exercises {: #page-templates-exercises}

### Tracing execution {: .exercise}

Add a directive `<span z-trace="variable"/>`
that prints the current value of a variable using `console.error` for debugging.

### Unit tests {: .exercise}

Write unit tests for template expansion using Mocha.

### Trimming text {: .exercise}

Modify all of the directives to take an extra optional attribute `z-trim="true"`
If this attribute is set,
leading and trailing whitespace is trimmed from the directive's expansion.

### Literal text {: .exercise}

Add a directive `<div z-literal="true">…</div>` that copies the enclosed text as-is
without interpreting or expanding any contained directives.
(A directive like this would be needed when writing documentation for the template expander.)

### Including other files {: .exercise}

1.  Add a directive `<div z-include="filename.html"/>` that includes another file
    in the file being processed.

2.  Should included files be processed and the result copied into the including file,
    or should the text be copied in and then processed?
    What difference does it make to the way variables are evaluated?

### HTML snippets {: .exercise}

Add a directive `<div z-snippet="variable">…</div>` that saves some text in a variable
so that it can be displayed later.
For example:

```html
<html>
  <body>
    <div z-snippet="prefix"><strong>Important:</strong></div>
    <p>Expect three items</p>
    <ul>
      <li z-loop="item:names">
        <span z-var="prefix"><span z-var="item"/>
      </li>
    </ul>
  </body>
</html>
```

would printed the word "Important:" in bold before each item in the list.
{: .continue}

### YAML headers {: .exercise}

Modify the template expander to handle variables defined in a YAML header in the page being processed.
For example, if the page is:

```html
---
name: "Dorothy Johnson Vaughan"
---
<html>
  <body>
    <p><span z-var="name"/></p>
  </body>
</html>
```

will create a paragraph containing the given name.
{: .continue}

### Expanding all files {: .exercise}

Write a program `expand-all.js` that takes two directory names as command-line arguments
and builds a website in the second directory by expanding all of the HTML files found in the first
or in sub-directories of the first.

### Counting loops {: .exercise}

Add a directive `<div z-index="indexName" z-limit="limitName">…</div>`
that loops from zero to the value in the variable `limitName`,
putting the current iteration index in `indexName`.

### Auxiliary functions {: .exercise}

1.  Modify `Expander` so that it takes an extra argument `auxiliaries`
    containing zero or more named functions:

    ```js
    const expander = new Expander(root, vars, {
      max: Math.max,
      trim: (x) => x.trim()
    })
    ```

2.  Add a directive `<span z-call="functionName" z-args="var,var"/>`
    that looks up a function in `auxiliaries` and calls it
    with the given variables as arguments.
