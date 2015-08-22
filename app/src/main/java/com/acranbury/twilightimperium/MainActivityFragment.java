package com.acranbury.twilightimperium;

import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.os.AsyncTask;
import android.os.Bundle;
import android.preference.PreferenceManager;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;

import com.google.android.gms.gcm.GoogleCloudMessaging;

import java.io.IOException;
import java.util.concurrent.atomic.AtomicInteger;


/**
 * A placeholder fragment containing a simple view.
 */
public class MainActivityFragment extends Fragment {

    public MainActivityFragment() {
    }

    private static final String SENDER_ID = "389849193267";
    private static final String TAG = "MainActivityFragment";

    private EditText mPlayerNameEditText;

    private GoogleCloudMessaging gcm;
    private AtomicInteger msgId;
    private String gameCode;

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View rootView = inflater.inflate(R.layout.fragment_main, container, false);

        mPlayerNameEditText = (EditText) rootView.findViewById(R.id.playerNameEditText);
        Button mNewGameButton = (Button) rootView.findViewById(R.id.newGameButton);
        Button mJoinGameButton = (Button) rootView.findViewById(R.id.joinGameButton);

        gcm = GoogleCloudMessaging.getInstance(getActivity());
        msgId = new AtomicInteger();

        mNewGameButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                SharedPreferences sharedPreferences =
                        PreferenceManager.getDefaultSharedPreferences(getActivity());
                String reg_id = sharedPreferences.getString(TwilightImperiumPreferences.REGISTRATION_TOKEN, "");

                Bundle data = new Bundle();
                data.putString("new_game", mPlayerNameEditText.getText().toString());
                data.putString("reg_id", reg_id);
                new GCMUpstreamTask().execute(data);
            }
        });

        mJoinGameButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());
                builder.setTitle(R.string.join_game_button);

                // Set up the input
                final EditText input = new EditText(getActivity());
                builder.setView(input);

                builder.setMessage(R.string.join_game_dialog);

                // Set up the buttons
                builder.setPositiveButton("OK", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        gameCode = input.getText().toString();

                        SharedPreferences sharedPreferences =
                                PreferenceManager.getDefaultSharedPreferences(getActivity());
                        String reg_id = sharedPreferences.getString(TwilightImperiumPreferences.REGISTRATION_TOKEN, "");

                        Bundle data = new Bundle();
                        data.putString("join_game", gameCode);
                        data.putString("player_name", mPlayerNameEditText.getText().toString());
                        data.putString("reg_id", reg_id);
                        new GCMUpstreamTask().execute(data);
                    }
                });
                builder.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.cancel();
                    }
                });

                builder.show();
            }
        });
        return rootView;
    }

    private class GCMUpstreamTask extends AsyncTask<Bundle,Void,String> {

        @Override
        protected String doInBackground(Bundle... params){
            String msg;
            try {
                String id = Integer.toString(msgId.incrementAndGet());
                params[0].putString("action",
                        "com.google.android.gcm.demo.app.ECHO_NOW");
                gcm.send(SENDER_ID + "@gcm.googleapis.com", id, params[0]);
                msg = "Sent message";
            } catch (IOException ex) {
                msg = "Error :" + ex.getMessage();
            }
            return msg;
        }

        @Override
        protected void onPostExecute(String msg) {
            //mPlayerNameEditText.append(msg + "\n");
            Log.i(TAG, msg);
        }
    }


}
