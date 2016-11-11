#!/bin/bash                                              
                                                         
# Get latest code                                        
git pull origin master
                                                         
# Update packets                                         
pip install -r requirements.txt                          
                                                         
# Install any compontnets that might have come in        
python manage.py bower_install -F                         
                                                         
# Collect static                                         
python manage.py collectstatic --noinput                 
                                                         
# Apply databse changes                                  
python manage.py migrate --noinput                       
                                                         
                                                         
# Restart services                                       
sudo initctl restart seshdash                            
                                                         
sudo initctl restart sesh-clry                           

ACCESS_TOKEN=
ENVIRONMENT=production
LOCAL_USERNAME=`whoami`
REVISION=`git log -n 1 --pretty=format:"%H"`

curl https://api.rollbar.com/api/1/deploy/ \
      -F access_token=$ACCESS_TOKEN \
      -F environment=$ENVIRONMENT \
      -F revision=$REVISION \
      -F local_username=$LOCAL_USERNAME
