# **1. How many commands did I have to run before it worked?**
1: Because I already had my local Python environment set up with  `matplotlib`, `pandas`, and `torch` from previous coursework, I did not have to run a series of `pip install` commands.
2 : needed to upgrade `pytorch` 

# 2. What libraries were missing? Did version mismatches cause errors?** 
In my case, the required libraries were already installed, including and PyTorch.

There were no missing libraries. However, version mismatches (with PyTorch) so it needed an upgrade
# **3. Did the model produce the same result? If not, why? (Random seeds, data shuffling, etc.)**

1: The code produced an accuracy of 53% 

![alt text](image.png)

2: The results were different because the model used random initialization (random seeds were not fixed).

# 4. If this had to run on a server at 3:00 AM, would it survive?
No it would fail if the server experiences a network timeout at 3:00 AM 
