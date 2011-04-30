def call_bayes(text)
  # call bayesian filter
  result = nil
  if text != nil
    p 'call bayesian filter'
    cmd='python /home/showyou/message_naive_bayes_classifier/main.py '+text
    IO.popen(cmd,'r+') do |io|
      result = io.gets
    end
  end
  return result
end
p call_bayes("RT: ほげ")

# $ ruby call_bayes.rb 
# "call bayesian filter"
# "0.271413779317\n"
