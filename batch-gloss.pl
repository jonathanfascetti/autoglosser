#!/usr/bin/perl

#Inputs: storyboard-datafile, english-sentence (without quotes)
($file,@inputs) = @ARGV;

$inputstring = join(" ",@inputs);


open (FILE,$file);
@lines = <FILE>;
close(FILE);

#warn scalar(@lines) . " lines\n";

$header = $lines[0];
chomp($header);
($idfield,@fields) = split(/\t/,$header);

#$numfields = scalar(@fields);
#warn $numfields;
#warn join ("|",@fields);

for($i = 1; $i < scalar(@lines); $i++) {

  $line = $lines[$i];
  chomp($line);
  ($idval,@values) = split(/\t/,$line);

  #warn scalar(@values);

  for ($j = 0; $j < scalar(@fields); $j++) {
    $key = $fields[$j];
    $value = $values[$j];
    $code = $key;
    $sentence = $key;
    if ($key =~ m/\|/) {
      ($code,$sentence) = split(/\|/,$key);
      #warn "code $code sentence $sentence";
    } 
    $promptmap{$code} = $sentence;
    
    #warn "j: " . $j;
    #warn "key: " . $key;
    #warn "value: " . $value;
    #warn "idval: " . $idval;
    $data{$code}{$idval} = $value;
  }
  
}

@answers = keys %{$data{$inputstring}};

# warn scalar(@answers);

#print "Input: $inputstring\n";

$prompt = $promptmap{$inputstring};
#print "Prompt: $prompt\n";

print "\n\\paragraph{$prompt [$inputstring]}\n";

foreach $index (sort @answers) {
  $value = $data{$inputstring}{$index};
  $input = lc($value);
  $input =~ s/\(/\\\(/g;
  $input =~ s/\)/\\\)/g;

  #make sure there's a space before the question mark
  $input =~ s/([^ ])\?/$1 \?/;

  #make sure there's a space before the period
  #  $input =~ s/([^ ])\./$1 \./;

  #strip final periods
  $input =~ s/\.[ ]*$//;
  
  system("python3 translate-beta.py -m $input > batch-gloss-temp.txt");
  open (FILE, "batch-gloss-temp.txt");
  $readglossnext = 0;
  $gloss = "";
  while (<FILE>) {
    if ($readglossnext>0&&$readglossnext<4) {
      $gloss[$readglossnext] = $_;
      $readglossnext++;
    }
    elsif ($readglossnext >=4) {
      last;
    } else {
      if (/LaTeX Gloss:/) {
	$readglossnext = 1;
      }
    }
  }
  close (FILE);
  system("rm -f batch-gloss-temp.txt");
  $index =~ s/&/\\&/;
  print  join("",@gloss) . "($inputstring:$index)\\\\\n";
  print "\%Original spelling: $value\n";
}

print "\n";
