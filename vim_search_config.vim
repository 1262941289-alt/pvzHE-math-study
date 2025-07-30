
" 高级搜索集成
" 添加到 ~/.vimrc 或 ~/.config/nvim/init.vim

" 搜索当前词
nnoremap <leader>fs :!python ./workspace_jumper.py <cword><CR>

" 搜索选中文本
vnoremap <leader>fs y:!python ./workspace_jumper.py <C-R>"<CR>

" 交互式搜索
nnoremap <leader>fi :!python ./workspace_jumper.py 

" 正则搜索
nnoremap <leader>fr :!python ./search_engine.py -r 

" 模糊搜索
nnoremap <leader>ff :!python ./search_engine.py -f 

" 函数：在Vim中打开搜索结果
function! OpenSearchResult(file, line)
    execute 'edit ' . a:file
    execute a:line
endfunction
