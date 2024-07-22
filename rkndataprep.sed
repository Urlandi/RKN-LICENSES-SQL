:begin;
/<rkn:record>/{
:newline;
 N;
 /<\/rkn:record>/{
  s/\s*\(\r\n\|\n\)\s*//g;
  s/<\(\/\)\?rkn:/<\1/g
  s/^\s*//;
  h;
  s/<\/record>.*/<\/record>/;
  p;
  g;
  s/.*<\/record>//;
  b begin;
 };
 b newline;
};
:stop;