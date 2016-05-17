#!/bin/bash                                              
                                                         
# Get latest code                                        
git pull origin                                          
                                                         
# Update packets                                         
pip install -r requirements.txt                          
                                                         
# Install any compontnets that might have come in        
python manage.py bower_install                           
                                                         
# Collect static                                         
python manage.py collectstatic --noinput                 
                                                         
# Apply databse changes                                  
python manage.py migrate --noinput                       
                                                         
                                                         
# Restart services                                       
sudo initctl restart seshdash                            
                                                         
sudo initctl restart sesh-clry                           
~                                                        
