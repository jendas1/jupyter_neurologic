define(['nbextensions/neurologic_highlighter/codemirror_grammar',
        'codemirror/lib/codemirror',
        'nbextensions/neurologic_highlighter/neurologic_grammar',
        'notebook/js/codecell'
    ],
    function (CodeMirrorGrammar, CodeMirror, neurologic_grammar, codecell) {
        var neurologic_mode = CodeMirrorGrammar.getMode(neurologic_grammar);

        CodeMirror.defineMode("text/x-neurologic", neurologic_mode);

        CodeMirror.defineMIME("text/x-neurologic", {
            name: "text/x-neurologic",
            mime: "text/x-neurologic",
            mode: "text/x-neurologic",
            ext: ".pl"
        });
        codecell.CodeCell.options_default.highlight_modes['magic_text/x-neurologic'] = {'reg': [/^%%writefile .*\.pl/]};
        Jupyter.notebook.events.one('kernel_ready.Kernel', function () {
            Jupyter.notebook.get_cells().map(function (cell) {
                if (cell.cell_type === 'code') {
                    cell.auto_highlight();
                }
            });
        });
    });